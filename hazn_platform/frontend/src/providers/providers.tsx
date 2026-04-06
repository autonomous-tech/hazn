"use client";

/**
 * Root providers wrapper.
 *
 * Wraps children with:
 * - QueryClientProvider (TanStack Query with staleTime: 0 for SSE-invalidated queries)
 * - ThemeProvider (next-themes with light default and dark mode support)
 * - TooltipProvider (required by shadcn/ui Tooltip component)
 * - Toaster (sonner toast notifications)
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { Toaster } from "sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  // Create QueryClient per component instance to avoid sharing state between requests
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // staleTime: 0 ensures SSE cache invalidation triggers immediate refetch
            staleTime: 0,
            // Retry once on failure, with exponential backoff
            retry: 1,
            // Don't refetch on window focus (SSE handles real-time updates)
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider
        attribute="class"
        defaultTheme="light"
        enableSystem
        disableTransitionOnChange
      >
        <TooltipProvider delayDuration={300}>
          {children}
          <Toaster
            position="bottom-right"
            richColors
            closeButton
            duration={5000}
          />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
