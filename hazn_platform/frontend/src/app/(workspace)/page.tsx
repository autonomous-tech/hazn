"use client";

/**
 * Dashboard landing page.
 *
 * Combines StatusCards + ActivityTimeline.
 * Respects selectedClientId from client-switcher to filter data.
 */

import { StatusCards } from "@/components/dashboard/status-cards";
import { ActivityTimeline } from "@/components/dashboard/activity-timeline";
import { useClientScope } from "@/hooks/use-client-scope";

export default function DashboardPage() {
  const { selectedClientId, hasClientFilter } = useClientScope();

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          {hasClientFilter
            ? "Showing activity for selected client"
            : "Overview of your workspace activity"}
        </p>
      </div>

      <StatusCards />
      <ActivityTimeline />
    </div>
  );
}
