"use client";

/**
 * SSE subscription hook with TanStack Query cache invalidation.
 *
 * Subscribes to SSE channels and automatically invalidates
 * relevant TanStack Query caches when events arrive. Also
 * increments the notification store unread count for user-facing
 * events.
 */

import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { createSSEConnection, type SSEEvent } from "@/lib/sse";
import { useNotificationStore } from "@/stores/notification-store";

/**
 * Subscribe to SSE channels and invalidate relevant queries on events.
 *
 * Event type -> query key mapping:
 * - workflow_status   -> ['workflows', run_id] + ['dashboard']
 * - chat_message      -> ['chat', run_id] + ['workflows', run_id]
 * - deliverable_ready -> ['deliverables']
 * - cost_update       -> ['workflows', run_id]
 */
export function useSSE(channels: string[]) {
  const queryClient = useQueryClient();
  const incrementUnread = useNotificationStore((s) => s.incrementUnread);

  useEffect(() => {
    if (channels.length === 0) return;

    const cleanup = createSSEConnection(channels, (event: SSEEvent) => {
      switch (event.type) {
        case "workflow_status":
          queryClient.invalidateQueries({
            queryKey: ["workflows", event.run_id],
          });
          queryClient.invalidateQueries({ queryKey: ["workflows"] });
          queryClient.invalidateQueries({ queryKey: ["dashboard"] });
          // Notify on completion or failure
          if (event.status === "completed" || event.status === "failed") {
            incrementUnread();
          }
          break;

        case "chat_message":
          queryClient.invalidateQueries({
            queryKey: ["chat", event.run_id],
          });
          queryClient.invalidateQueries({
            queryKey: ["workflows", event.run_id],
          });
          break;

        case "deliverable_ready":
          queryClient.invalidateQueries({ queryKey: ["deliverables"] });
          queryClient.invalidateQueries({ queryKey: ["dashboard"] });
          incrementUnread();
          break;

        case "cost_update":
          queryClient.invalidateQueries({
            queryKey: ["workflows", event.run_id],
          });
          break;

        default:
          // Unknown event type -- invalidate dashboard as a fallback
          queryClient.invalidateQueries({ queryKey: ["dashboard"] });
          break;
      }
    });

    return cleanup;
  }, [channels, queryClient, incrementUnread]);
}
