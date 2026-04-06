/**
 * Next.js 16 proxy -- rewrites /api/* requests to the Django backend.
 *
 * This eliminates CORS issues by making all API calls same-origin
 * from the browser's perspective. The proxy forwards cookies and
 * headers to Django, enabling session-based auth.
 *
 * @see https://nextjs.org/docs/app/api-reference/file-conventions/proxy
 */
import { NextResponse, type NextRequest } from "next/server";

const DJANGO_API_URL =
  process.env.DJANGO_API_URL || "http://localhost:8000";

export function proxy(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith("/api/")) {
    const url = new URL(
      request.nextUrl.pathname + request.nextUrl.search,
      DJANGO_API_URL,
    );
    return NextResponse.rewrite(url);
  }
}

export const config = {
  matcher: "/api/:path*",
};
