"use client";

/**
 * Workflow run monitoring page.
 *
 * Layout:
 * - Phase stepper at top
 * - Chat-style log below (workflow-chat.tsx)
 * - Cost tracker in header area
 * - Cancel button with confirmation
 * - Clone and Re-run button
 */

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft,
  Copy,
  Loader2,
  Square,
  Play,
} from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";

import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { WorkflowChat } from "@/components/workflow/workflow-chat";
import {
  PhaseStepper,
  type PhaseStep,
} from "@/components/workflow/phase-stepper";
import { CostTracker } from "@/components/workflow/cost-tracker";
import type { WorkflowRunDetail, WorkflowTriggerResponse } from "@/types/api";

export default function WorkflowRunPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const runId = params.id;

  const [showCancelDialog, setShowCancelDialog] = useState(false);

  // Fetch workflow run detail
  const { data: run, isLoading } = useQuery({
    queryKey: ["workflows", runId],
    queryFn: () =>
      api.get<WorkflowRunDetail>(`/workspace/workflows/${runId}/`),
  });

  // Cancel mutation
  const cancelMutation = useMutation({
    mutationFn: () =>
      api.post(`/workspace/workflows/${runId}/cancel/`),
    onSuccess: () => {
      toast.success("Workflow cancelled");
      setShowCancelDialog(false);
      queryClient.invalidateQueries({ queryKey: ["workflows", runId] });
    },
    onError: () => toast.error("Failed to cancel workflow"),
  });

  // Clone and re-run mutation
  const cloneMutation = useMutation({
    mutationFn: () =>
      api.post<WorkflowTriggerResponse>(
        `/workspace/workflows/${runId}/clone/`
      ),
    onSuccess: (data) => {
      toast.success("Workflow cloned and launched");
      if (data.celery_task_id) {
        router.push(`/workflows/${data.celery_task_id}`);
      }
    },
    onError: () => toast.error("Failed to clone workflow"),
  });

  // Build phase stepper data
  const phases: PhaseStep[] = run
    ? run.phase_outputs.map((po, idx) => ({
        id: po.phase_id,
        label: po.phase_id.replace(/_/g, " "),
        status:
          idx < run.phase_outputs.length - 1
            ? "completed"
            : run.status === "running"
              ? "running"
              : run.status === "failed"
                ? "failed"
                : "completed",
      }))
    : [];

  const isRunning = run?.status === "running" || run?.status === "waiting_for_input";
  const isTerminal =
    run?.status === "completed" ||
    run?.status === "failed" ||
    run?.status === "timed_out";

  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!run) {
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <p className="text-muted-foreground">Workflow run not found</p>
        <Button variant="link" asChild className="mt-2">
          <Link href="/workflows">Back to Workflows</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b px-6 py-4">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon-sm" asChild>
            <Link href="/workflows">
              <ArrowLeft className="size-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-lg font-bold">{run.workflow_name}</h1>
            <p className="text-xs text-muted-foreground">
              Triggered by {run.triggered_by}
            </p>
          </div>
          <Badge
            variant={
              run.status === "completed"
                ? "default"
                : run.status === "failed"
                  ? "destructive"
                  : "secondary"
            }
          >
            {isRunning && (
              <Loader2 className="mr-1 size-3 animate-spin" />
            )}
            {run.status}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          {/* Cost tracker */}
          <CostTracker currentCost={run.total_cost} />

          {/* Cancel button (only when running) */}
          {isRunning && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowCancelDialog(true)}
            >
              <Square className="size-4" />
              Cancel
            </Button>
          )}

          {/* Clone and Re-run (only when terminal) */}
          {isTerminal && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => cloneMutation.mutate()}
              disabled={cloneMutation.isPending}
            >
              {cloneMutation.isPending ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Copy className="size-4" />
              )}
              Clone & Re-run
            </Button>
          )}
        </div>
      </div>

      {/* Phase stepper */}
      {phases.length > 0 && (
        <div className="border-b px-6">
          <PhaseStepper phases={phases} />
        </div>
      )}

      {/* Chat view */}
      <div className="flex-1 overflow-y-auto">
        <WorkflowChat runId={runId} />
      </div>

      {/* Cancel confirmation dialog */}
      <Dialog open={showCancelDialog} onOpenChange={setShowCancelDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel workflow</DialogTitle>
            <DialogDescription>
              Are you sure you want to cancel this workflow? Partial learnings
              will be preserved.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowCancelDialog(false)}
              disabled={cancelMutation.isPending}
            >
              Keep Running
            </Button>
            <Button
              variant="destructive"
              onClick={() => cancelMutation.mutate()}
              disabled={cancelMutation.isPending}
            >
              {cancelMutation.isPending ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Square className="size-4" />
              )}
              Cancel Workflow
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
