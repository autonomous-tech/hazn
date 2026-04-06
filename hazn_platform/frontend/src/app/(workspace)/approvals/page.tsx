"use client";

/**
 * Approvals page -- vestigial from v1.0 HITL system.
 * HITL was removed in v3.0. Shows an informational empty state.
 */

export default function ApprovalsPage() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <p className="text-lg font-medium text-muted-foreground">
        Approvals are not available in this version.
      </p>
      <p className="mt-2 text-sm text-muted-foreground">
        Workflow runs no longer require manual approval steps.
      </p>
    </div>
  );
}
