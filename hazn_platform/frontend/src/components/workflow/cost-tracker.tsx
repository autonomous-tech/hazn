"use client";

/**
 * Live cost tracker for workflow runs.
 *
 * Compact display showing: current cost (updating via SSE), estimated
 * range bar, warning indicator if approaching max threshold. Uses
 * amber/red colors as cost increases.
 */

import { DollarSign, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

interface CostTrackerProps {
  /** Current cost as string (from DRF decimal serialization) */
  currentCost: string;
  /** Estimated cost range [low, high] */
  estimatedRange?: [string, string];
  /** Agency's max cost threshold */
  maxThreshold?: string;
}

export function CostTracker({
  currentCost,
  estimatedRange,
  maxThreshold,
}: CostTrackerProps) {
  const cost = parseFloat(currentCost) || 0;
  const max = maxThreshold ? parseFloat(maxThreshold) : undefined;
  const estLow = estimatedRange ? parseFloat(estimatedRange[0]) : undefined;
  const estHigh = estimatedRange ? parseFloat(estimatedRange[1]) : undefined;

  // Determine warning level
  const warningLevel =
    max && cost > max * 0.9
      ? "critical"
      : max && cost > max * 0.7
        ? "warning"
        : "normal";

  // Calculate position on range bar
  const rangeMax = max || estHigh || cost * 2 || 1;
  const costPct = Math.min((cost / rangeMax) * 100, 100);

  return (
    <div className="flex items-center gap-3 rounded-lg border bg-card px-4 py-2">
      <DollarSign
        className={cn(
          "size-4",
          warningLevel === "critical"
            ? "text-red-500"
            : warningLevel === "warning"
              ? "text-amber-500"
              : "text-muted-foreground"
        )}
      />

      <div className="flex-1 space-y-1">
        <div className="flex items-center justify-between">
          <span
            className={cn(
              "text-sm font-semibold tabular-nums",
              warningLevel === "critical"
                ? "text-red-500"
                : warningLevel === "warning"
                  ? "text-amber-500"
                  : "text-foreground"
            )}
          >
            ${cost.toFixed(2)}
          </span>

          {estHigh && (
            <span className="text-xs text-muted-foreground">
              est. ${estLow?.toFixed(2)}-${estHigh.toFixed(2)}
            </span>
          )}
        </div>

        {/* Cost range bar */}
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
          <div
            className={cn(
              "h-full rounded-full transition-all duration-500",
              warningLevel === "critical"
                ? "bg-red-500"
                : warningLevel === "warning"
                  ? "bg-amber-500"
                  : "bg-primary"
            )}
            style={{ width: `${costPct}%` }}
          />
        </div>

        {max && (
          <div className="flex items-center justify-end gap-1">
            {warningLevel !== "normal" && (
              <AlertTriangle className="size-3 text-amber-500" />
            )}
            <span className="text-[10px] text-muted-foreground">
              max: ${parseFloat(maxThreshold!).toFixed(2)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
