"use client";

/**
 * Deliverable card component.
 *
 * Shows deliverable name, task type badge, end-client, and date.
 * Click navigates to detail page.
 */

import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { FileText } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Deliverable } from "@/types/api";

interface DeliverableCardProps {
  deliverable: Deliverable;
}

export function DeliverableCard({ deliverable }: DeliverableCardProps) {
  return (
    <Link href={`/deliverables/${deliverable.id}`}>
      <Card className="h-full transition-shadow hover:shadow-md">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-start gap-3">
              <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                <FileText className="size-4 text-primary" />
              </div>
              <div>
                <CardTitle className="text-sm leading-tight">
                  {deliverable.title}
                </CardTitle>
                <p className="mt-1 text-xs text-muted-foreground">
                  {deliverable.task_type.replace(/_/g, " ")}
                </p>
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-3 pt-0">
          {/* Date */}
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-xs">
              Ready
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground">
            {formatDistanceToNow(new Date(deliverable.created_at), {
              addSuffix: true,
            })}
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}
