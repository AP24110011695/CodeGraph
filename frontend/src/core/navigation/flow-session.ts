const FLOW_SESSION_KEY = 'codegraph-active-flow';

type FlowSession =
  | { kind: 'upload' }
  | { kind: 'indexing'; repositoryId: string };

function readSession(): FlowSession | null {
  try {
    const value = window.sessionStorage.getItem(FLOW_SESSION_KEY);
    return value ? (JSON.parse(value) as FlowSession) : null;
  } catch {
    return null;
  }
}

function writeSession(session: FlowSession): void {
  window.sessionStorage.setItem(FLOW_SESSION_KEY, JSON.stringify(session));
}

export function beginUploadFlow(): void {
  writeSession({ kind: 'upload' });
}

export function beginIndexingFlow(repositoryId: string): void {
  writeSession({ kind: 'indexing', repositoryId });
}

export function hasUploadFlow(): boolean {
  return readSession()?.kind === 'upload';
}

export function hasIndexingFlow(repositoryId: string): boolean {
  const session = readSession();
  return session?.kind === 'indexing' && session.repositoryId === repositoryId;
}

export function clearFlowSession(): void {
  window.sessionStorage.removeItem(FLOW_SESSION_KEY);
}

/** Remove the legacy persisted store that could reopen a stale route after restart. */
export function clearLegacyRoutingState(): void {
  window.localStorage.removeItem('codegraph-repository');
}
