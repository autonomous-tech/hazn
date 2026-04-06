"use client";

/**
 * Deliverables list page.
 *
 * Shows deliverables in a responsive grid with filters.
 * Respects client-switcher scope. Real-time SSE updates.
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { FileText } from "lucide-react";

import { api } from "@/lib/api";
import { useClientScope } from "@/hooks/use-client-scope";
import { useSSE } from "@/hooks/use-sse";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { DeliverableCard } from "@/components/deliverables/deliverable-card";
import type {
  Deliverable,
  EndClient,
  PaginatedResponse,
} from "@/types/api";

const TASK_TYPE_OPTIONS = [
  { value: "all", label: "All types" },
  { value: "blog_post", label: "Blog Post" },
  { value: "landing_page", label: "Landing Page" },
  { value: "email_template", label: "Email Template" },
  { value: "social_post", label: "Social Post" },
  { value: "audit_report", label: "Audit Report" },
];

export default function DeliverablesPage() {
  const { selectedClientId } = useClientScope();

  // Filters
  const [clientFilter, setClientFilter] = useState(
    selectedClientId || "all"
  );
  const [taskTypeFilter, setTaskTypeFilter] = useState("all");

  // SSE for new deliverables
  useSSE(["deliverables"]);

  // Fetch clients for filter
  const { data: clientsData } = useQuery({
    queryKey: ["clients"],
    queryFn: () =>
      api.get<PaginatedResponse<EndClient>>("/workspace/clients/"),
  });
  const clients = clientsData?.results ?? [];

  // Build query params
  const params = new URLSearchParams();
  if (clientFilter !== "all") params.set("end_client", clientFilter);
  if (taskTypeFilter !== "all") params.set("task_type", taskTypeFilter);
  const queryString = params.toString();

  // Fetch deliverables
  const { data: deliverablesData, isLoading } = useQuery({
    queryKey: ["deliverables", clientFilter, taskTypeFilter],
    queryFn: () =>
      api.get<PaginatedResponse<Deliverable>>(
        `/workspace/deliverables/${queryString ? `?${queryString}` : ""}`
      ),
  });

  const deliverables = deliverablesData?.results ?? [];

  return (
    <div className="space-y-6 p-6">
      {/* Page header */}
      <div className="flex items-center gap-3">
        <FileText className="size-6 text-primary" />
        <div>
          <h1 className="text-2xl font-bold">Deliverables</h1>
          <p className="text-sm text-muted-foreground">
            Review, approve, and share agent-generated outputs
          </p>
        </div>
      </div>

      {/* Filter bar */}
      <div className="flex flex-wrap gap-3">
        <Select value={clientFilter} onValueChange={setClientFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="End-client" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All clients</SelectItem>
            {clients.map((client) => (
              <SelectItem key={client.id} value={client.id}>
                {client.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={taskTypeFilter} onValueChange={setTaskTypeFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Task type" />
          </SelectTrigger>
          <SelectContent>
            {TASK_TYPE_OPTIONS.map((t) => (
              <SelectItem key={t.value} value={t.value}>
                {t.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="space-y-3 rounded-xl border p-6">
              <div className="flex gap-3">
                <Skeleton className="size-9 rounded-lg" />
                <div className="flex-1 space-y-1">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-3 w-20" />
                </div>
              </div>
              <Skeleton className="h-5 w-24" />
              <Skeleton className="h-3 w-16" />
            </div>
          ))}
        </div>
      )}

      {/* Deliverables grid */}
      {!isLoading && deliverables.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {deliverables.map((d) => (
            <DeliverableCard key={d.id} deliverable={d} />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && deliverables.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-16">
          <FileText className="mb-4 size-12 text-muted-foreground/40" />
          <p className="max-w-sm text-center text-sm text-muted-foreground">
            No deliverables yet. Deliverables are created when workflow agents
            produce content outputs.
          </p>
        </div>
      )}
    </div>
  );
}
