"use client";

/**
 * Hook for reading and setting the selected end-client scope.
 *
 * Uses the zustand UI store to track which end-client is currently
 * selected. "All clients" is represented by null. All workspace
 * views use this hook to scope API queries.
 */

import { useUIStore } from "@/stores/ui-store";

export function useClientScope() {
  const selectedClientId = useUIStore((s) => s.selectedClientId);
  const setSelectedClient = useUIStore((s) => s.setSelectedClient);

  return {
    /** Currently selected end-client ID, or null for "All clients" */
    selectedClientId,
    /** Set the selected end-client (pass null for "All clients") */
    setSelectedClient,
    /** Whether a specific client is selected (vs "All clients") */
    hasClientFilter: selectedClientId !== null,
  };
}
