/**
 * SSE (Server-Sent Events) client utility.
 *
 * Creates an EventSource connection to the Django SSE endpoint
 * with channel-based multiplexing. Returns a cleanup function
 * for React effect teardown.
 *
 * Uses a single connection with multiple channels to stay within
 * the browser's 6-connection-per-origin limit.
 */

export interface SSEEvent {
  type: string;
  [key: string]: unknown;
}

export type SSEEventHandler = (event: SSEEvent) => void;

/**
 * Create an SSE connection to the given channels.
 * Returns a cleanup function that closes the connection.
 *
 * @param channels - Channel names to subscribe to (e.g., ["agency-{id}"])
 * @param onMessage - Callback for each received message
 * @param onError - Optional error callback
 */
export function createSSEConnection(
  channels: string[],
  onMessage: SSEEventHandler,
  onError?: (error: Event) => void,
): () => void {
  if (channels.length === 0) {
    return () => {};
  }

  const params = channels.map((c) => `channel=${encodeURIComponent(c)}`).join("&");
  const url = `/api/events/?${params}`;

  const source = new EventSource(url);

  source.onmessage = (event: MessageEvent) => {
    try {
      const data: SSEEvent = JSON.parse(event.data);
      onMessage(data);
    } catch {
      // Ignore non-JSON messages (e.g., keep-alive pings)
    }
  };

  if (onError) {
    source.onerror = onError;
  }

  return () => {
    source.close();
  };
}
