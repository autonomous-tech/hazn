import type { NextConfig } from "next";

const DJANGO_API_URL =
  process.env.DJANGO_API_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  /* Prevent 308 redirects that strip trailing slashes from Django URLs */
  skipTrailingSlashRedirect: true,

  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${DJANGO_API_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
