"use client";

/**
 * TanStack Query hook for authentication state.
 *
 * Wraps checkAuth() to provide reactive auth state with
 * loading indicator and user data.
 */

import { useQuery } from "@tanstack/react-query";
import { checkAuth } from "@/lib/auth";

export interface AuthUser {
  id: number;
  email: string;
  username: string;
  display: string;
  hasUsablePassword: boolean;
}

export function useAuth() {
  const { data: session, isLoading, error } = useQuery({
    queryKey: ["auth", "session"],
    queryFn: checkAuth,
    staleTime: 5 * 60 * 1000, // 5 minutes -- session doesn't change frequently
    retry: false,
  });

  const user: AuthUser | null = session?.data?.user
    ? {
        id: session.data.user.id,
        email: session.data.user.email,
        username: session.data.user.username,
        display: session.data.user.display,
        hasUsablePassword: session.data.user.has_usable_password,
      }
    : null;

  return {
    user,
    isLoading,
    isAuthenticated: !!session?.meta?.is_authenticated,
    error,
    /** Auth methods used (e.g., password, socialaccount) */
    methods: session?.data?.methods ?? [],
  };
}
