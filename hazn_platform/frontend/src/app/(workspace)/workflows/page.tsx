"use client";

/**
 * Workflow catalog page.
 *
 * Shows available workflow types as cards with guided trigger dialog.
 * Below the catalog, shows recent workflow runs with status badges.
 */

import { useQuery } from "@tanstack/react-query";
import { Play, Loader2 } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import Link from "next/link";

import { api } from "@/lib/api";
import { useClientScope } from "@/hooks/use-client-scope";
import { useSSE } from "@/hooks/use-sse";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  WorkflowCard,
  type WorkflowType,
} from "@/components/workflow/workflow-card";
import type { WorkflowRun, PaginatedResponse } from "@/types/api";

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
  running: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  completed:
    "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  failed: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  timed_out:
    "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  waiting_for_input:
    "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
};

export default function WorkflowsPage() {
  const { selectedClientId } = useClientScope();

  // SSE for workflow updates
  useSSE(["workflows"]);

  // Fetch workflow catalog
  const { data: catalog, isLoading: catalogLoading } = useQuery({
    queryKey: ["workflows", "catalog"],
    queryFn: () =>
      api.get<WorkflowType[]>("/workspace/workflows/catalog/"),
  });

  // Fetch recent workflow runs
  const runsParams = selectedClientId
    ? `?end_client=${selectedClientId}`
    : "";
  const { data: runsData, isLoading: runsLoading } = useQuery({
    queryKey: ["workflows", "runs", selectedClientId],
    queryFn: () =>
      api.get<WorkflowRun[] | PaginatedResponse<WorkflowRun>>(
        `/workspace/workflows/${runsParams}`
      ),
  });

  const runs = Array.isArray(runsData) ? runsData : runsData?.results ?? [];

  return (
    <div className="space-y-8 p-6">
      {/* Page header */}
      <div className="flex items-center gap-3">
        <Play className="size-6 text-primary" />
        <div>
          <h1 className="text-2xl font-bold">Workflows</h1>
          <p className="text-sm text-muted-foreground">
            Browse available workflows and monitor running ones
          </p>
        </div>
      </div>

      {/* Workflow catalog */}
      <section>
        <h2 className="mb-4 text-lg font-semibold">Workflow Catalog</h2>

        {catalogLoading && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-3 rounded-xl border p-6">
                <Skeleton className="h-5 w-32" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-9 w-full" />
              </div>
            ))}
          </div>
        )}

        {catalog && catalog.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {catalog.map((wf) => (
              <WorkflowCard key={wf.name} workflow={wf} />
            ))}
          </div>
        )}

        {catalog && catalog.length === 0 && (
          <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-16">
            <Play className="mb-4 size-12 text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground">
              No workflows configured yet.
            </p>
          </div>
        )}
      </section>

      {/* Recent workflow runs */}
      <section>
        <h2 className="mb-4 text-lg font-semibold">Recent Runs</h2>

        {runsLoading && (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-14 w-full rounded-lg" />
            ))}
          </div>
        )}

        {runs.length > 0 && (
          <div className="space-y-2">
            {runs.map((run) => (
              <Link
                key={run.id}
                href={`/workflows/${run.id}`}
                className="flex items-center justify-between rounded-lg border px-4 py-3 transition-colors hover:bg-accent"
              >
                <div className="flex items-center gap-3">
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">
                      {run.workflow_name}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(run.created_at), {
                        addSuffix: true,
                      })}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs tabular-nums text-muted-foreground">
                    ${parseFloat(run.total_cost).toFixed(2)}
                  </span>
                  <Badge
                    className={
                      STATUS_COLORS[run.status] || STATUS_COLORS.pending
                    }
                    variant="outline"
                  >
                    {run.status === "running" && (
                      <Loader2 className="mr-1 size-3 animate-spin" />
                    )}
                    {run.status}
                  </Badge>
                </div>
              </Link>
            ))}
          </div>
        )}

        {!runsLoading && runs.length === 0 && (
          <p className="py-8 text-center text-sm text-muted-foreground">
            No workflow runs yet. Launch your first workflow from the catalog above.
          </p>
        )}
      </section>
    </div>
  );
}
