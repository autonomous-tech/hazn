/**
 * Reusable empty state component.
 *
 * Friendly illustration (emoji or SVG), title, description,
 * and optional CTA button. "Add your first end-client",
 * "Run your first workflow", etc.
 */

import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  title: string;
  description: string;
  emoji?: string;
  actionLabel?: string;
  onAction?: () => void;
  actionHref?: string;
  className?: string;
}

export function EmptyState({
  title,
  description,
  emoji = "📋",
  actionLabel,
  onAction,
  actionHref,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center py-12 text-center ${className || ""}`}
    >
      <div className="mb-4 text-5xl" role="img" aria-label={title}>
        {emoji}
      </div>
      <h3 className="mb-1 text-lg font-semibold">{title}</h3>
      <p className="mb-6 max-w-sm text-sm text-muted-foreground">
        {description}
      </p>
      {actionLabel && (
        <>
          {actionHref ? (
            <Button asChild className="rounded-lg">
              <a href={actionHref}>{actionLabel}</a>
            </Button>
          ) : onAction ? (
            <Button onClick={onAction} className="rounded-lg">
              {actionLabel}
            </Button>
          ) : null}
        </>
      )}
    </div>
  );
}
