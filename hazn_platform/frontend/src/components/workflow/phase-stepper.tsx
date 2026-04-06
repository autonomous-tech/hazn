"use client";

/**
 * Horizontal phase stepper for workflow runs.
 *
 * Shows workflow phases as steps: current phase highlighted,
 * completed phases with checkmark, failed phases with X.
 * Clickable to scroll chat to that phase's messages.
 */

import { Check, X, Circle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export interface PhaseStep {
  id: string;
  label: string;
  status: "pending" | "running" | "completed" | "failed";
}

interface PhaseStepperProps {
  phases: PhaseStep[];
  /** Callback when a phase step is clicked */
  onPhaseClick?: (phaseId: string) => void;
}

export function PhaseStepper({ phases, onPhaseClick }: PhaseStepperProps) {
  if (phases.length === 0) return null;

  return (
    <div className="flex items-center gap-1 overflow-x-auto px-1 py-2">
      {phases.map((phase, index) => (
        <div key={phase.id} className="flex items-center">
          {/* Connector line */}
          {index > 0 && (
            <div
              className={cn(
                "h-px w-6 shrink-0",
                phase.status === "pending"
                  ? "bg-muted"
                  : phase.status === "failed"
                    ? "bg-red-300"
                    : "bg-primary/40"
              )}
            />
          )}

          {/* Step */}
          <button
            onClick={() => onPhaseClick?.(phase.id)}
            className={cn(
              "flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors",
              phase.status === "completed" &&
                "border-primary/30 bg-primary/10 text-primary",
              phase.status === "running" &&
                "border-primary bg-primary/5 text-primary ring-2 ring-primary/20",
              phase.status === "failed" &&
                "border-red-300 bg-red-50 text-red-600 dark:bg-red-950/30",
              phase.status === "pending" &&
                "border-muted bg-muted/50 text-muted-foreground",
              onPhaseClick && "cursor-pointer hover:bg-accent"
            )}
          >
            {phase.status === "completed" && (
              <Check className="size-3 text-primary" />
            )}
            {phase.status === "running" && (
              <Loader2 className="size-3 animate-spin text-primary" />
            )}
            {phase.status === "failed" && (
              <X className="size-3 text-red-500" />
            )}
            {phase.status === "pending" && (
              <Circle className="size-3 text-muted-foreground" />
            )}
            <span className="whitespace-nowrap">{phase.label}</span>
          </button>
        </div>
      ))}
    </div>
  );
}
