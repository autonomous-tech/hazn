/**
 * Zustand store for notification bell state.
 *
 * Tracks unread notification count, incremented by SSE events.
 * The count resets when the user opens the notification dropdown.
 *
 * No persistence -- unread count resets on page refresh (by design,
 * since the bell fetches current state from the API).
 */

import { create } from "zustand";

interface NotificationState {
  /** Number of unread notification items */
  unreadCount: number;

  /** Increment unread count (called from SSE event handler) */
  incrementUnread: () => void;
  /** Reset unread count (called when notification dropdown opens) */
  resetUnread: () => void;
}

export const useNotificationStore = create<NotificationState>()((set) => ({
  unreadCount: 0,

  incrementUnread: () =>
    set((state) => ({ unreadCount: state.unreadCount + 1 })),

  resetUnread: () => set({ unreadCount: 0 }),
}));
