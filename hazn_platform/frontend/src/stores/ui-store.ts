/**
 * Zustand store for UI-only state.
 *
 * Manages sidebar collapsed state (persisted to localStorage)
 * and the currently selected end-client for scoping views.
 *
 * Server data belongs in TanStack Query -- this store is for
 * client-only UI preferences.
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface UIState {
  /** Whether the sidebar is collapsed to icon-only mode */
  sidebarCollapsed: boolean;
  /** Currently selected end-client ID, or null for "All clients" */
  selectedClientId: string | null;

  /** Toggle sidebar between expanded and collapsed */
  toggleSidebar: () => void;
  /** Set the sidebar collapsed state directly */
  setSidebarCollapsed: (collapsed: boolean) => void;
  /** Set the selected end-client (pass null for "All clients") */
  setSelectedClient: (clientId: string | null) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      selectedClientId: null,

      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

      setSidebarCollapsed: (collapsed: boolean) =>
        set({ sidebarCollapsed: collapsed }),

      setSelectedClient: (clientId: string | null) =>
        set({ selectedClientId: clientId }),
    }),
    {
      name: "hazn-ui-preferences",
      // Only persist sidebar preference, not client selection
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    },
  ),
);
