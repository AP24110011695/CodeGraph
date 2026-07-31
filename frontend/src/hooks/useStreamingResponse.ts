/**
 * SSE / EventSource streaming hook.
 * Implemented in the Copilot phase — foundation stub only.
 */
export function useStreamingResponse(): {
  content: string;
  isStreaming: boolean;
  error: Error | null;
} {
  return {
    content: '',
    isStreaming: false,
    error: null,
  };
}
