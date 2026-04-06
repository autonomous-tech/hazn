"use client";

/**
 * Auth layout -- centered card for login/signup pages.
 * No sidebar, no header. Clean branded feel with Hazn logo.
 */

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-background via-background to-primary/5 px-4">
      <div className="mb-8 flex flex-col items-center gap-2">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-primary-foreground font-bold text-xl">
          H
        </div>
        <h1 className="text-2xl font-bold tracking-tight">Hazn</h1>
        <p className="text-sm text-muted-foreground">
          AI-powered marketing workspace
        </p>
      </div>
      <div className="w-full max-w-md">{children}</div>
    </div>
  );
}
