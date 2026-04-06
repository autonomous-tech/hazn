"use client";

/**
 * Editable memory block card.
 *
 * Displays a memory block with metadata (creation date, source workflow,
 * confidence score). Craft learnings (archival) support inline editing.
 * Client context and persona blocks are read-only with a lock icon.
 */

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import {
  ChevronDown,
  ChevronUp,
  Lock,
  Pencil,
  Save,
  X,
  Workflow,
  Calendar,
  Gauge,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import type { MemoryBlock } from "@/types/api";

interface MemoryBlockCardProps {
  block: MemoryBlock;
  /** Whether this block is editable (craft learnings only) */
  editable?: boolean;
  /** Whether the card is selected for bulk actions */
  selected?: boolean;
  /** Callback for checkbox toggle */
  onSelectToggle?: (id: string) => void;
}

/** Determine if a block is a craft learning (archival) based on metadata */
function isCraftLearning(block: MemoryBlock): boolean {
  const meta = block.metadata;
  if (!meta) return false;
  const source = (meta.source as string) || "";
  const blockType = (meta.block_type as string) || "";
  return (
    source.includes("craft") ||
    source.includes("archival") ||
    blockType === "archival" ||
    blockType === "craft_learning"
  );
}

export function MemoryBlockCard({
  block,
  editable = true,
  selected = false,
  onSelectToggle,
}: MemoryBlockCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(block.text);
  const queryClient = useQueryClient();

  const canEdit = editable && isCraftLearning(block);
  const isReadOnly = !isCraftLearning(block);

  const correctMutation = useMutation({
    mutationFn: (correctedText: string) =>
      api.post("/workspace/memory/correct/", {
        block_id: block.id,
        corrected_text: correctedText,
      }),
    onSuccess: () => {
      toast.success("Memory corrected successfully");
      queryClient.invalidateQueries({ queryKey: ["memory"] });
      setIsEditing(false);
    },
    onError: () => {
      toast.error("Failed to correct memory");
    },
  });

  const handleSave = () => {
    if (editText.trim() && editText !== block.text) {
      correctMutation.mutate(editText);
    } else {
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setEditText(block.text);
    setIsEditing(false);
  };

  const isLongContent = block.text.length > 200;
  const displayText =
    isLongContent && !isExpanded ? block.text.slice(0, 200) + "..." : block.text;

  const confidence = block.metadata?.confidence as number | undefined;
  const sourceWorkflow = block.metadata?.workflow_name as string | undefined;

  return (
    <Card
      className={cn(
        "transition-shadow hover:shadow-md",
        selected && "ring-2 ring-primary"
      )}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start gap-3">
          {/* Bulk select checkbox */}
          {onSelectToggle && (
            <input
              type="checkbox"
              checked={selected}
              onChange={() => onSelectToggle(block.id)}
              className="mt-1 size-4 rounded border-input"
            />
          )}

          <div className="flex-1 space-y-1">
            {/* Block type badge + lock icon for read-only */}
            <div className="flex items-center gap-2">
              {isCraftLearning(block) ? (
                <Badge variant="secondary" className="text-xs">
                  Craft Learning
                </Badge>
              ) : (
                <Badge variant="outline" className="text-xs">
                  <Lock className="mr-1 size-3" />
                  {(block.metadata?.block_type as string) || "Context"}
                </Badge>
              )}

              {confidence !== undefined && (
                <span className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Gauge className="size-3" />
                  {Math.round(confidence * 100)}%
                </span>
              )}

              {block.score !== undefined && (
                <span className="text-xs text-muted-foreground">
                  Relevance: {(block.score * 100).toFixed(0)}%
                </span>
              )}
            </div>

            {/* Metadata row */}
            <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
              {block.created_at && (
                <span className="flex items-center gap-1">
                  <Calendar className="size-3" />
                  {formatDistanceToNow(new Date(block.created_at), {
                    addSuffix: true,
                  })}
                </span>
              )}
              {sourceWorkflow && (
                <span className="flex items-center gap-1">
                  <Workflow className="size-3" />
                  {sourceWorkflow}
                </span>
              )}
            </div>
          </div>

          {/* Edit button for craft learnings */}
          {canEdit && !isEditing && (
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={() => setIsEditing(true)}
            >
              <Pencil className="size-3" />
            </Button>
          )}

          {/* Read-only lock indicator */}
          {isReadOnly && (
            <Lock className="size-4 text-muted-foreground" />
          )}
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {isEditing ? (
          <div className="space-y-2">
            <Textarea
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              rows={4}
              className="resize-y"
            />
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={handleSave}
                disabled={correctMutation.isPending}
              >
                <Save className="size-3" />
                {correctMutation.isPending ? "Saving..." : "Save"}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleCancel}
                disabled={correctMutation.isPending}
              >
                <X className="size-3" />
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <div>
            <p className="whitespace-pre-wrap text-sm">{displayText}</p>
            {isLongContent && (
              <Button
                variant="ghost"
                size="xs"
                className="mt-1"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? (
                  <>
                    <ChevronUp className="size-3" /> Show less
                  </>
                ) : (
                  <>
                    <ChevronDown className="size-3" /> Show more
                  </>
                )}
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
