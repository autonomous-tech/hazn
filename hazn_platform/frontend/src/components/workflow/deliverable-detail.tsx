"use client";

/**
 * Deliverable detail component for rendering branded HTML reports.
 *
 * Fetches a deliverable by ID and renders its html_content inline via
 * an iframe using srcDoc. Provides an "Open Report" button that links
 * to the backend HTML endpoint for full-page viewing.
 *
 * Security: iframe uses sandbox="allow-same-origin" to prevent script
 * execution in the rendered report content.
 */

import { useQuery } from "@tanstack/react-query";
import { ExternalLink, FileText, Loader2 } from "lucide-react";

import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import type { Deliverable } from "@/types/api";

interface DeliverableDetailProps {
  deliverableId: string;
}

export function DeliverableDetail({ deliverableId }: DeliverableDetailProps) {
  const { data: deliverable, isLoading } = useQuery({
    queryKey: ["deliverables", deliverableId],
    queryFn: () =>
      api.get<Deliverable>(`/workspace/deliverables/${deliverableId}/`),
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-9 w-28" />
        </div>
        <Skeleton className="h-[600px] w-full rounded-lg" />
      </div>
    );
  }

  if (!deliverable) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
        <FileText className="mb-2 size-8 text-muted-foreground/40" />
        <p className="text-sm">Deliverable not found</p>
      </div>
    );
  }

  if (!deliverable.html_content) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
        <FileText className="mb-2 size-8 text-muted-foreground/40" />
        <p className="text-sm">No rendered report available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">{deliverable.title}</h3>
        <Button variant="outline" size="sm" asChild>
          <a
            href={`/api/workspace/deliverables/${deliverableId}/html/`}
            target="_blank"
            rel="noopener noreferrer"
          >
            <ExternalLink className="mr-1 size-4" />
            Open Report
          </a>
        </Button>
      </div>
      {/* Inline iframe preview -- srcDoc renders HTML without a separate request */}
      <iframe
        srcDoc={deliverable.html_content}
        className="h-[600px] w-full rounded-lg border"
        title={deliverable.title}
        sandbox="allow-same-origin"
      />
    </div>
  );
}
