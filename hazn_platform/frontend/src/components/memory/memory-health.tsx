"use client";

/**
 * Memory health stats display.
 *
 * Shows total memories count, last updated date (relative time),
 * and a simple age distribution bar (green/yellow/red).
 */

import { formatDistanceToNow } from "date-fns";
import { Activity, Clock, Database } from "lucide-react";
import type { MemoryBlock } from "@/types/api";

interface MemoryHealthProps {
  blocks: MemoryBlock[];
}

function computeAgeDistribution(blocks: MemoryBlock[]) {
  const now = Date.now();
  let fresh = 0;
  let aging = 0;
  let stale = 0;

  for (const block of blocks) {
    if (!block.created_at) {
      stale++;
      continue;
    }
    const ageMs = now - new Date(block.created_at).getTime();
    const ageDays = ageMs / (1000 * 60 * 60 * 24);

    if (ageDays < 7) {
      fresh++;
    } else if (ageDays < 30) {
      aging++;
    } else {
      stale++;
    }
  }

  return { fresh, aging, stale };
}

export function MemoryHealth({ blocks }: MemoryHealthProps) {
  const total = blocks.length;

  if (total === 0) {
    return null;
  }

  const { fresh, aging, stale } = computeAgeDistribution(blocks);
  const freshPct = Math.round((fresh / total) * 100);
  const agingPct = Math.round((aging / total) * 100);
  const stalePct = 100 - freshPct - agingPct;

  // Find most recently created block
  const lastUpdated = blocks.reduce<string | null>((latest, b) => {
    if (!b.created_at) return latest;
    if (!latest) return b.created_at;
    return new Date(b.created_at) > new Date(latest) ? b.created_at : latest;
  }, null);

  return (
    <div className="flex flex-wrap items-center gap-6 rounded-lg border bg-card px-5 py-3">
      {/* Total memories */}
      <div className="flex items-center gap-2">
        <Database className="size-4 text-muted-foreground" />
        <span className="text-sm font-medium">{total}</span>
        <span className="text-sm text-muted-foreground">memories</span>
      </div>

      {/* Last updated */}
      {lastUpdated && (
        <div className="flex items-center gap-2">
          <Clock className="size-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">
            Updated{" "}
            {formatDistanceToNow(new Date(lastUpdated), { addSuffix: true })}
          </span>
        </div>
      )}

      {/* Age distribution bar */}
      <div className="flex items-center gap-2">
        <Activity className="size-4 text-muted-foreground" />
        <div className="flex h-2 w-32 overflow-hidden rounded-full bg-muted">
          {freshPct > 0 && (
            <div
              className="bg-green-500 transition-all"
              style={{ width: `${freshPct}%` }}
            />
          )}
          {agingPct > 0 && (
            <div
              className="bg-yellow-500 transition-all"
              style={{ width: `${agingPct}%` }}
            />
          )}
          {stalePct > 0 && (
            <div
              className="bg-red-500 transition-all"
              style={{ width: `${stalePct}%` }}
            />
          )}
        </div>
        <div className="flex gap-2 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <span className="inline-block size-2 rounded-full bg-green-500" />
            {fresh}
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block size-2 rounded-full bg-yellow-500" />
            {aging}
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block size-2 rounded-full bg-red-500" />
            {stale}
          </span>
        </div>
      </div>
    </div>
  );
}
