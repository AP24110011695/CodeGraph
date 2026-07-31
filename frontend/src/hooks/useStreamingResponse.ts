/**
 * SSE / EventSource streaming hook.
 * Copilot currently uses JSON POST /copilot/chat.
 * This hook remains the future integration point for token streaming.
 */
export function useStreamingResponse(): {
  content: string;
  isStreaming: boolean;
  error: Error | null;
  start: (url: string) => void;
  stop: () => void;
} {
  return {
    content: '',
    isStreaming: false,
    error: null,
    start: (url: string) => {
      void url;
      // no-op until backend exposes SSE
    },
    stop: () => {
      // no-op
    },
  };
}
