"use client";

/**
 * Interactive chat-style workflow monitoring view.
 *
 * Bidirectional chat: user can send messages (initial inputs, steering),
 * agent posts questions and output. Real-time via SSE + polling fallback.
 *
 * Features:
 * - Chat input bar at bottom for sending messages
 * - Pre-run prompt for initial inputs (CHAT-02)
 * - Agent pause indicator (waiting_for_input)
 * - User message bubbles (right-aligned)
 * - Agent/system messages from API merged with phase output context
 */

import { useEffect, useRef, useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Bot,
  FileText,
  AlertCircle,
  CheckCircle2,
  Loader2,
  Send,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { api } from "@/lib/api";
import { useSSE } from "@/hooks/use-sse";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import type {
  WorkflowRunDetail,
  WorkflowPhaseOutput,
  ChatMessage as APIChatMessage,
} from "@/types/api";

interface WorkflowChatProps {
  runId: string;
}

/**
 * Chat message types derived from workflow run data and API chat messages.
 */
type ChatMessage =
  | { type: "phase_transition"; phaseId: string; label: string; timestamp: string }
  | { type: "agent_message"; agentType: string; content: string; timestamp: string }
  | { type: "user_message"; content: string; timestamp: string }
  | { type: "deliverable"; output: WorkflowPhaseOutput; timestamp: string }
  | { type: "error"; phaseId: string; error: string; timestamp: string }
  | { type: "status_change"; status: string; timestamp: string };

/**
 * Build supplementary chat messages from phase outputs (transitions, deliverables, errors).
 */
function buildPhaseMessages(run: WorkflowRunDetail): ChatMessage[] {
  const messages: ChatMessage[] = [];

  for (const output of run.phase_outputs) {
    const isFailed =
      output.content?.status === "failed" ||
      output.content?.error != null;

    messages.push({
      type: "phase_transition",
      phaseId: output.phase_id,
      label: output.phase_id.replace(/_/g, " "),
      timestamp: output.created_at,
    });

    if (isFailed) {
      const errorText =
        typeof output.content?.error === "string"
          ? output.content.error
          : typeof output.content?.error_details === "string"
            ? output.content.error_details
            : `Phase ${output.phase_id} failed`;
      messages.push({
        type: "error",
        phaseId: output.phase_id,
        error: errorText,
        timestamp: output.created_at,
      });
    }

    if (output.output_type === "deliverable" || output.content?.html) {
      messages.push({
        type: "deliverable",
        output,
        timestamp: output.created_at,
      });
    }
  }

  // Check run-level error_details
  if (
    run.error_details &&
    typeof run.error_details === "object" &&
    Object.keys(run.error_details).length > 0
  ) {
    const errorPhaseIds = new Set(
      messages.filter((m) => m.type === "error").map((m) => (m as { phaseId: string }).phaseId),
    );
    const errorMsg =
      typeof run.error_details.error === "string"
        ? run.error_details.error
        : typeof run.error_details.message === "string"
          ? (run.error_details.message as string)
          : null;
    if (errorMsg && errorPhaseIds.size === 0) {
      messages.push({
        type: "error",
        phaseId: "workflow",
        error: errorMsg,
        timestamp: run.ended_at || run.created_at,
      });
    }
  }

  return messages;
}

/**
 * Convert API ChatMessage records to internal ChatMessage format.
 */
function apiToChatMessages(apiMessages: APIChatMessage[]): ChatMessage[] {
  return apiMessages.map((msg) => {
    if (msg.role === "user") {
      return {
        type: "user_message" as const,
        content: msg.content,
        timestamp: msg.created_at,
      };
    }
    return {
      type: "agent_message" as const,
      agentType: msg.role === "system" ? "system" : "agent",
      content: msg.content,
      timestamp: msg.created_at,
    };
  });
}

export function WorkflowChat({ runId }: WorkflowChatProps) {
  const chatEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();
  const [inputValue, setInputValue] = useState("");

  // Fetch workflow run detail
  const { data: run, isLoading } = useQuery({
    queryKey: ["workflows", runId],
    queryFn: () =>
      api.get<WorkflowRunDetail>(`/workspace/workflows/${runId}/`),
    refetchInterval: (query) => {
      const data = query.state.data;
      if (
        data?.status === "completed" ||
        data?.status === "failed" ||
        data?.status === "timed_out"
      ) {
        return false;
      }
      return 5000;
    },
  });

  // Fetch chat messages from API (primary source)
  const { data: chatMessages = [] } = useQuery({
    queryKey: ["chat", runId],
    queryFn: () =>
      api.get<APIChatMessage[]>(`/workspace/runs/${runId}/chat/`),
    refetchInterval: (query) => {
      // Stop polling on terminal status
      if (
        run?.status === "completed" ||
        run?.status === "failed" ||
        run?.status === "timed_out"
      ) {
        return false;
      }
      return 3000; // 3-second backup polling
    },
  });

  // Subscribe to SSE for real-time updates
  const agencyId = run?.agency;
  useSSE(agencyId ? [`agency-${agencyId}`] : []);

  // Send message mutation
  const sendMessage = useMutation({
    mutationFn: (content: string) =>
      api.post<APIChatMessage>(`/workspace/runs/${runId}/chat/`, {
        content,
        role: "user",
      }),
    onSuccess: () => {
      setInputValue("");
      queryClient.invalidateQueries({ queryKey: ["chat", runId] });
      queryClient.invalidateQueries({ queryKey: ["workflows", runId] });
    },
  });

  // Merge API chat messages with phase output context messages
  const messages = useMemo(() => {
    if (!run) return [];

    const apiMsgs = apiToChatMessages(chatMessages);
    const phaseMsgs = buildPhaseMessages(run);

    const allMessages = [...apiMsgs, ...phaseMsgs];

    // Sort by timestamp
    allMessages.sort(
      (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    // Add final status if terminal
    if (run.status === "completed" || run.status === "failed") {
      allMessages.push({
        type: "status_change",
        status: run.status,
        timestamp: run.ended_at || run.created_at,
      });
    }

    return allMessages;
  }, [run, chatMessages]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  const isTerminal =
    run?.status === "completed" ||
    run?.status === "failed" ||
    run?.status === "timed_out";

  const isWaitingForInput = run?.status === "waiting_for_input";
  const isPending = run?.status === "pending";
  const hasUserMessages = chatMessages.some((m) => m.role === "user");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = inputValue.trim();
    if (!trimmed || sendMessage.isPending) return;
    sendMessage.mutate(trimmed);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4 p-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex gap-3">
            <Skeleton className="size-8 shrink-0 rounded-full" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-3 w-24" />
              <Skeleton className="h-16 w-full rounded-lg" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!run) {
    return (
      <div className="flex items-center justify-center py-16 text-muted-foreground">
        Workflow run not found
      </div>
    );
  }

  // Determine input placeholder
  const placeholder =
    isPending && !hasUserMessages
      ? "Enter site URL, company name, or any context to get started..."
      : isWaitingForInput
        ? "Type your response to the agent..."
        : "Send a message to steer the agent...";

  return (
    <div className="flex h-full flex-col">
      {/* Messages area */}
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {/* Pre-run welcome for pending runs with no user messages */}
        {isPending && !hasUserMessages && messages.length === 0 && (
          <div className="flex gap-3">
            <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
              <Bot className="size-4 text-primary" />
            </div>
            <div className="flex-1">
              <div className="mb-1 flex items-center gap-2">
                <span className="text-xs font-medium">Agent</span>
              </div>
              <div className="rounded-lg rounded-tl-none border bg-card px-3 py-2">
                <p className="text-sm">
                  Welcome! Please provide the initial inputs for this workflow.
                  You can share a site URL, company name, or any relevant context
                  to get started.
                </p>
              </div>
            </div>
          </div>
        )}

        {!isPending && messages.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
            <Loader2 className="mb-2 size-6 animate-spin" />
            <p className="text-sm">Waiting for agent activity...</p>
          </div>
        )}

        {messages.map((msg, idx) => {
          switch (msg.type) {
            case "phase_transition":
              return (
                <PhaseTransitionMarker
                  key={`phase-${idx}`}
                  label={msg.label}
                />
              );

            case "agent_message":
              return (
                <AgentBubble
                  key={`msg-${idx}`}
                  agentType={msg.agentType}
                  content={msg.content}
                  timestamp={msg.timestamp}
                />
              );

            case "user_message":
              return (
                <UserBubble
                  key={`user-${idx}`}
                  content={msg.content}
                  timestamp={msg.timestamp}
                />
              );

            case "deliverable":
              return (
                <DeliverableCard
                  key={`del-${idx}`}
                  output={msg.output}
                />
              );

            case "error":
              return (
                <ErrorBubble
                  key={`err-${idx}`}
                  phaseId={msg.phaseId}
                  error={msg.error}
                  timestamp={msg.timestamp}
                />
              );

            case "status_change":
              return (
                <StatusMarker
                  key={`status-${idx}`}
                  status={msg.status}
                  timestamp={msg.timestamp}
                />
              );

            default:
              return null;
          }
        })}

        {/* Waiting for input indicator */}
        {isWaitingForInput && (
          <div className="flex items-center gap-2 px-3 py-2">
            <span className="relative flex size-2">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-amber-400 opacity-75" />
              <span className="relative inline-flex size-2 rounded-full bg-amber-500" />
            </span>
            <span className="text-sm text-amber-600 dark:text-amber-400">
              Agent is waiting for your input...
            </span>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Chat input bar */}
      {!isTerminal && (
        <div className="border-t bg-background px-4 py-3">
          <form onSubmit={handleSubmit} className="flex items-end gap-2">
            <Textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={sendMessage.isPending}
              className="min-h-10 max-h-32 resize-none"
              rows={1}
            />
            <Button
              type="submit"
              size="icon"
              disabled={!inputValue.trim() || sendMessage.isPending}
              className="shrink-0"
            >
              {sendMessage.isPending ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Send className="size-4" />
              )}
            </Button>
          </form>
        </div>
      )}
    </div>
  );
}

/* --- Sub-components --- */

function PhaseTransitionMarker({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-3 py-2">
      <div className="h-px flex-1 bg-border" />
      <Badge variant="outline" className="text-xs font-medium capitalize">
        {label}
      </Badge>
      <div className="h-px flex-1 bg-border" />
    </div>
  );
}

function AgentBubble({
  agentType,
  content,
  timestamp,
}: {
  agentType: string;
  content: string;
  timestamp: string;
}) {
  const label = agentType.replace(/_/g, " ");

  return (
    <div className="flex gap-3">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
        <Bot className="size-4 text-primary" />
      </div>
      <div className="flex-1">
        <div className="mb-1 flex items-center gap-2">
          <span className="text-xs font-medium capitalize">{label}</span>
          <span className="text-[10px] text-muted-foreground">
            {formatDistanceToNow(new Date(timestamp), { addSuffix: true })}
          </span>
        </div>
        <div className="rounded-lg rounded-tl-none border bg-card px-3 py-2">
          <p className="whitespace-pre-wrap text-sm">{content}</p>
        </div>
      </div>
    </div>
  );
}

function UserBubble({ content, timestamp }: { content: string; timestamp: string }) {
  return (
    <div className="flex gap-3 justify-end">
      <div className="flex-1 max-w-[80%]">
        <div className="mb-1 flex items-center gap-2 justify-end">
          <span className="text-[10px] text-muted-foreground">
            {formatDistanceToNow(new Date(timestamp), { addSuffix: true })}
          </span>
          <span className="text-xs font-medium">You</span>
        </div>
        <div className="rounded-lg rounded-tr-none border bg-primary/5 px-3 py-2">
          <p className="whitespace-pre-wrap text-sm">{content}</p>
        </div>
      </div>
    </div>
  );
}

function ErrorBubble({
  phaseId,
  error,
  timestamp,
}: {
  phaseId: string;
  error: string;
  timestamp: string;
}) {
  return (
    <div className="flex gap-3">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-destructive/10">
        <AlertCircle className="size-4 text-destructive" />
      </div>
      <div className="flex-1">
        <div className="mb-1 flex items-center gap-2">
          <span className="text-xs font-medium text-destructive">
            {phaseId.replace(/_/g, " ")} failed
          </span>
          <span className="text-[10px] text-muted-foreground">
            {formatDistanceToNow(new Date(timestamp), { addSuffix: true })}
          </span>
        </div>
        <div className="rounded-lg rounded-tl-none border border-destructive/30 bg-destructive/5 px-3 py-2">
          <p className="whitespace-pre-wrap font-mono text-xs text-destructive">
            {error}
          </p>
        </div>
      </div>
    </div>
  );
}

function DeliverableCard({ output }: { output: WorkflowPhaseOutput }) {
  const deliverableId = output.content?.deliverable_id as string | undefined;
  const hasHtml = !!output.content?.html_content || !!output.content?.html;

  return (
    <div className="ml-11">
      <Card className="border-primary/20 bg-primary/5">
        <CardContent className="flex items-center gap-3 px-4 py-3">
          <FileText className="size-5 text-primary" />
          <div className="flex-1">
            <p className="text-sm font-medium">
              Deliverable: {output.summary || output.output_type}
            </p>
            <p className="text-xs text-muted-foreground">
              {output.phase_id.replace(/_/g, " ")}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {hasHtml && deliverableId && (
              <Button variant="outline" size="xs" asChild>
                <a
                  href={`/api/workspace/deliverables/${deliverableId}/html/`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View Report
                </a>
              </Button>
            )}
            <Badge variant="secondary" className="text-xs">
              Ready
            </Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatusMarker({
  status,
  timestamp,
}: {
  status: string;
  timestamp: string;
}) {
  const isSuccess = status === "completed";
  return (
    <div className="flex items-center gap-3 py-2">
      <div className="h-px flex-1 bg-border" />
      <Badge
        variant={isSuccess ? "default" : "destructive"}
        className="text-xs"
      >
        {isSuccess ? (
          <CheckCircle2 className="mr-1 size-3" />
        ) : (
          <AlertCircle className="mr-1 size-3" />
        )}
        Workflow {status}
      </Badge>
      <div className="h-px flex-1 bg-border" />
    </div>
  );
}
