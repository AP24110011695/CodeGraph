/**
 * Frontend analytics stub. No-op until a telemetry provider is configured.
 */
export function trackEvent(event: string, properties?: Record<string, unknown>): void {
  void event;
  void properties;
}

export function identifyUser(userId: string, traits?: Record<string, unknown>): void {
  void userId;
  void traits;
}

export function resetAnalytics(): void {
  // no-op
}
