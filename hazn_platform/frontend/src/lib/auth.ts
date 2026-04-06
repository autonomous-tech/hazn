/**
 * Auth helpers for django-allauth headless mode.
 *
 * All auth flows go through the allauth headless browser API:
 * - Email + password login
 * - Magic link (login by code)
 * - OAuth social login (Google, Facebook, Apple)
 * - Session check + logout
 */

const ALLAUTH_BASE = "/api/_allauth/browser/v1";

function getCsrfToken(): string {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : "";
}

interface AllAuthSession {
  status: number;
  data: {
    user: {
      id: number;
      display: string;
      has_usable_password: boolean;
      email: string;
      username: string;
    };
    methods: Array<{
      method: string;
      at: number;
      email?: string;
      provider?: string;
    }>;
  };
  meta: {
    is_authenticated: boolean;
    session_token?: string;
    access_token?: string;
  };
}

interface AllAuthError {
  status: number;
  errors: Array<{
    message: string;
    code: string;
    param?: string;
  }>;
}

export type AuthResponse = AllAuthSession | AllAuthError;

/**
 * Check current authentication session.
 * Returns session data if authenticated, null otherwise.
 */
export async function checkAuth(): Promise<AllAuthSession | null> {
  try {
    const response = await fetch(`${ALLAUTH_BASE}/auth/session`, {
      credentials: "include",
    });

    if (!response.ok) {
      return null;
    }

    const data: AllAuthSession = await response.json();
    return data.meta?.is_authenticated ? data : null;
  } catch {
    return null;
  }
}

/**
 * Ensure CSRF cookie is set before making a POST request.
 */
async function ensureCsrf(): Promise<string> {
  let token = getCsrfToken();
  if (!token) {
    await fetch(`${ALLAUTH_BASE}/config`, { credentials: "include" });
    token = getCsrfToken();
  }
  return token;
}

/**
 * Login with email and password.
 */
export async function login(
  email: string,
  password: string,
): Promise<AuthResponse> {
  const csrf = await ensureCsrf();
  const response = await fetch(`${ALLAUTH_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
    credentials: "include",
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    if (data && "errors" in data) return data;
    return { status: response.status, errors: [{ message: "Login failed", code: "unknown" }] };
  }

  return response.json();
}

/**
 * Request a magic link (login by code) for the given email.
 * The user will receive an email with a code to complete login.
 */
export async function requestMagicLink(email: string): Promise<AuthResponse> {
  const response = await fetch(`${ALLAUTH_BASE}/auth/code/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrfToken() },
    credentials: "include",
    body: JSON.stringify({ email }),
  });

  return response.json();
}

/**
 * Confirm a magic link code to complete login.
 */
export async function confirmMagicLink(code: string): Promise<AuthResponse> {
  const response = await fetch(`${ALLAUTH_BASE}/auth/code/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrfToken() },
    credentials: "include",
    body: JSON.stringify({ code }),
  });

  return response.json();
}

/**
 * Sign up with email and password.
 */
export async function signup(
  email: string,
  password: string,
  name?: string,
): Promise<AuthResponse> {
  const response = await fetch(`${ALLAUTH_BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrfToken() },
    credentials: "include",
    body: JSON.stringify({
      email,
      password,
      ...(name ? { name } : {}),
    }),
  });

  return response.json();
}

/**
 * Logout (delete session).
 */
export async function logout(): Promise<void> {
  await fetch(`${ALLAUTH_BASE}/auth/session`, {
    method: "DELETE",
    headers: { "X-CSRFToken": getCsrfToken() },
    credentials: "include",
  });
}

/**
 * Redirect to OAuth social login flow.
 * The allauth callback URL handles the token exchange on Django side,
 * then redirects back to the SPA via HEADLESS_FRONTEND_URLS.
 */
export function socialLogin(
  provider: "google" | "facebook" | "apple",
  callbackUrl: string = "/",
): void {
  // allauth social login initiates from the Django server-side callback
  // The proxy rewrites this to Django which handles the OAuth redirect
  const redirectUrl = `/api/_allauth/browser/v1/auth/provider/redirect`;
  const params = new URLSearchParams({
    provider,
    callback_url: callbackUrl,
    process: "login",
  });

  if (typeof window !== "undefined") {
    window.location.href = `${redirectUrl}?${params.toString()}`;
  }
}
