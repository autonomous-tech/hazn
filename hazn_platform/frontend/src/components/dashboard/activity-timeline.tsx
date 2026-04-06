"use client";

/**
 * Activity timeline -- chronological feed of recent activity.
 *
 * Shows workflow completions, deliverables ready.
 * Each item: icon, description, relative timestamp, link to detail.
 * Empty state if no activity.
 */

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import { api } from "@/lib/api";
import { useClientScope } from "@/hooks/use-client-scope";
import type { DashboardData, ActivityItem } from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/empty-states/empty-state";
import {
  Play,
  FileText,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock,
} from "lucide-react";

function getActivityIcon(type: string) {
  switch (type) {
    case "workflow_started":
    case "workflow_running":
      return <Play className="h-4 w-4 text-blue-500" />;
    case "workflow_completed":
      return <CheckCircle className="h-4 w-4 text-emerald-500" />;
    case "workflow_failed":
      return <XCircle className="h-4 w-4 text-destructive" />;
    case "deliverable_ready":
      return <FileText className="h-4 w-4 text-emerald-500" />;
    case "cost_alert":
      return <AlertCircle className="h-4 w-4 text-destructive" />;
    default:
      return <Clock className="h-4 w-4 text-muted-foreground" />;
  }
}

function getActivityLink(item: ActivityItem): string | null {
  const id = item.id as string | undefined;
  switch (item.type) {
    case "workflow_started":
    case "workflow_running":
    case "workflow_completed":
    case "workflow_failed":
      return id ? `/workflows/${id}` : "/workflows";
    case "deliverable_ready":
      return id ? `/deliverables/${id}` : "/deliverables";
    default:
      return null;
  }
}

function ActivityTimelineItem({ item }: { item: ActivityItem }) {
  const link = getActivityLink(item);
  const timeAgo = formatDistanceToNow(new Date(item.timestamp), {
    addSuffix: true,
  });

  const content = (
    <div className="flex items-start gap-3 rounded-lg px-3 py-2.5 transition-colors hover:bg-accent/50">
      <div className="mt-0.5">{getActivityIcon(item.type)}</div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium leading-tight">{item.title}</p>
        <p className="text-xs text-muted-foreground mt-0.5">{timeAgo}</p>
      </div>
    </div>
  );

  if (link) {
    return <Link href={link}>{content}</Link>;
  }
  return content;
}

function TimelineSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="flex items-start gap-3 px-3 py-2.5">
          <Skeleton className="h-5 w-5 rounded-full mt-0.5" />
          <div className="flex-1 space-y-1.5">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-20" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function ActivityTimeline() {
  const { selectedClientId } = useClientScope();

  const { data, isLoading } = useQuery({
    queryKey: ["dashboard", selectedClientId],
    queryFn: () => {
      const params = selectedClientId
        ? `?end_client=${selectedClientId}`
        : "";
      return api.get<DashboardData>(`/workspace/dashboard/${params}`);
    },
  });

  const activities = data?.recent_activity || [];

  return (
    <Card className="rounded-xl">
      <CardHeader>
        <CardTitle className="text-base">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <TimelineSkeleton />
        ) : activities.length === 0 ? (
          <EmptyState
            title="No activity yet"
            description="Activity from your workflows will appear here"
            emoji="🕐"
          />
        ) : (
          <div className="space-y-1">
            {activities.map((item, i) => (
              <ActivityTimelineItem key={`${item.type}-${i}`} item={item} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
