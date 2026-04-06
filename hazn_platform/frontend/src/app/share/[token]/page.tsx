/**
 * Public share page at /share/{token}.
 *
 * NO authentication required. Server component that fetches deliverable
 * content by share token. Renders Hazn branding, deliverable HTML in
 * sandboxed iframe, and error states for expired/invalid tokens.
 */

interface ShareDeliverable {
  title: string;
  html_content: string;
  task_type: string;
  created_at: string;
}

const DJANGO_API =
  process.env.DJANGO_API_URL || "http://localhost:8001";

async function fetchShareDeliverable(
  token: string
): Promise<ShareDeliverable | null> {
  try {
    const res = await fetch(`${DJANGO_API}/api/share/${token}/`, {
      cache: "no-store",
    });

    if (res.status === 404) return null;
    if (res.status === 410) return null; // Expired

    if (!res.ok) return null;

    return res.json();
  } catch {
    return null;
  }
}

export default async function SharePage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = await params;
  const deliverable = await fetchShareDeliverable(token);

  if (!deliverable) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="space-y-4 text-center">
          {/* Hazn branding */}
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-primary-foreground text-xl font-bold">
            H
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Deliverable Not Found
          </h1>
          <p className="max-w-md text-gray-600 dark:text-gray-400">
            This share link may have expired or the deliverable may no longer
            be available.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-gray-50 dark:bg-gray-950">
      {/* Minimal header with Hazn branding */}
      <header className="border-b bg-white px-6 py-3 dark:bg-gray-900">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground text-sm font-bold">
              H
            </div>
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
              Shared Deliverable
            </span>
          </div>
        </div>
      </header>

      {/* Deliverable content */}
      <main className="mx-auto w-full max-w-5xl flex-1 p-6">
        <div className="mb-4">
          <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
            {deliverable.title}
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {deliverable.task_type.replace(/_/g, " ")}
          </p>
        </div>

        <div className="overflow-hidden rounded-lg border bg-white shadow-sm dark:bg-gray-900">
          <iframe
            srcDoc={deliverable.html_content}
            sandbox="allow-same-origin"
            className="h-[700px] w-full border-0"
            title={deliverable.title}
          />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white px-6 py-4 dark:bg-gray-900">
        <div className="mx-auto flex max-w-5xl items-center justify-center gap-2 text-xs text-gray-400">
          <div className="flex h-5 w-5 items-center justify-center rounded bg-primary/10 text-[10px] font-bold text-primary">
            H
          </div>
          Powered by Hazn
        </div>
      </footer>
    </div>
  );
}
