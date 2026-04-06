"use client";

/**
 * Deliverable detail page.
 *
 * Shows deliverable content rendered in a sandboxed iframe (srcdoc),
 * and share link generation.
 */

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  Share2,
  Calendar,
  Workflow,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import Link from "next/link";

import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ShareDialog } from "@/components/deliverables/share-dialog";
import type { Deliverable } from "@/types/api";

export default function DeliverableDetailPage() {
  const params = useParams<{ id: string }>();
  const deliverableId = params.id;
  const [showShareDialog, setShowShareDialog] = useState(false);

  // Fetch deliverable detail
  const { data: deliverable, isLoading } = useQuery({
    queryKey: ["deliverables", deliverableId],
    queryFn: () =>
      api.get<Deliverable>(`/workspace/deliverables/${deliverableId}/`),
  });

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center gap-3">
          <Skeleton className="size-8" />
          <Skeleton className="h-7 w-48" />
        </div>
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!deliverable) {
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <p className="text-muted-foreground">Deliverable not found</p>
        <Button variant="link" asChild className="mt-2">
          <Link href="/deliverables">Back to Deliverables</Link>
        </Button>
      </div>
    );
  }

  // Get HTML content from deliverable
  const htmlContent =
    deliverable.html_content ||
    (deliverable.preview_url ? null : "<p>No preview available</p>");

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <Button variant="ghost" size="icon-sm" asChild>
            <Link href="/deliverables">
              <ArrowLeft className="size-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-xl font-bold">{deliverable.title}</h1>
            <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <Calendar className="size-3" />
                {formatDistanceToNow(new Date(deliverable.created_at), {
                  addSuffix: true,
                })}
              </span>
              <span className="flex items-center gap-1">
                <Workflow className="size-3" />
                {deliverable.task_type.replace(/_/g, " ")}
              </span>
            </div>
          </div>
        </div>

        <Badge variant="secondary" className="text-xs">
          Ready
        </Badge>
      </div>

      {/* Action buttons */}
      <div className="flex gap-2">
        <Button
          variant="outline"
          onClick={() => setShowShareDialog(true)}
        >
          <Share2 className="size-4" />
          Share
        </Button>
      </div>

      {/* Deliverable content in sandboxed iframe */}
      <div className="overflow-hidden rounded-lg border">
        {htmlContent ? (
          <iframe
            srcDoc={htmlContent}
            sandbox="allow-same-origin"
            className="h-[600px] w-full border-0"
            title="Deliverable preview"
          />
        ) : deliverable.preview_url ? (
          <iframe
            src={deliverable.preview_url}
            sandbox="allow-same-origin allow-scripts"
            className="h-[600px] w-full border-0"
            title="Deliverable preview"
          />
        ) : (
          <div className="flex items-center justify-center py-24 text-muted-foreground">
            No preview available
          </div>
        )}
      </div>

      {/* Share dialog */}
      <ShareDialog
        deliverableId={deliverableId}
        open={showShareDialog}
        onOpenChange={setShowShareDialog}
      />
    </div>
  );
}
