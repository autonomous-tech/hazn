"use client";

/**
 * Dashboard status cards -- two cards in a responsive grid.
 *
 * - Running Workflows: count + "View" button -> /workflows
 * - Ready Deliverables: count + "View" button -> /deliverables
 *
 * Uses TanStack Query to fetch from /api/workspace/dashboard/.
 * Skeleton loading state. Friendly colors: blue, green.
 */

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useClientScope } from "@/hooks/use-client-scope";
import type { DashboardData } from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Play, FileText } from "lucide-react";

interface StatusCard {
  title: string;
  icon: React.ElementType;
  countKey: keyof Pick<
    DashboardData,
    "running_workflows" | "ready_deliverables"
  >;
  href: string;
  action: string;
  colorClass: string;
  iconBgClass: string;
}

const CARDS: StatusCard[] = [
  {
    title: "Running Workflows",
    icon: Play,
    countKey: "running_workflows",
    href: "/workflows",
    action: "View",
    colorClass: "text-blue-600 dark:text-blue-400",
    iconBgClass: "bg-blue-100 dark:bg-blue-950",
  },
  {
    title: "Ready Deliverables",
    icon: FileText,
    countKey: "ready_deliverables",
    href: "/deliverables",
    action: "View",
    colorClass: "text-emerald-600 dark:text-emerald-400",
    iconBgClass: "bg-emerald-100 dark:bg-emerald-950",
  },
];

function StatusCardSkeleton() {
  return (
    <Card className="rounded-xl">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-9 w-9 rounded-lg" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-8 w-12 mb-2" />
        <Skeleton className="h-8 w-16" />
      </CardContent>
    </Card>
  );
}

export function StatusCards() {
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

  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatusCardSkeleton />
        <StatusCardSkeleton />
        <StatusCardSkeleton />
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {CARDS.map((card) => {
        const Icon = card.icon;
        const count = data?.[card.countKey] ?? 0;
        return (
          <Card key={card.countKey} className="rounded-xl">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {card.title}
              </CardTitle>
              <div
                className={`flex h-9 w-9 items-center justify-center rounded-lg ${card.iconBgClass}`}
              >
                <Icon className={`h-4 w-4 ${card.colorClass}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${card.colorClass}`}>
                {count}
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="mt-1 -ml-2 h-8 text-xs"
                asChild
              >
                <Link href={card.href}>{card.action}</Link>
              </Button>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
