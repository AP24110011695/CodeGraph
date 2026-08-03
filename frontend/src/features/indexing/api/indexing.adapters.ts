import type {
  IndexResponse,
  IndexingSnapshot,
  IndexingStep,
  IndexingStepId,
  RepositoryStateEnum,
  RepositoryStateResponse,
  StepUiStatus,
} from './indexing.types';

const STEP_ORDER: IndexingStepId[] = [
  'scanning',
  'parsing',
  'indexing',
  'embedding',
  'analyzing',
  'ready',
];

const STEP_LABELS: Record<IndexingStepId, string> = {
  scanning: 'Scanning',
  parsing: 'Parsing',
  indexing: 'Indexing',
  embedding: 'Embedding',
  analyzing: 'Analyzing',
  ready: 'Ready',
};

const STATE_TO_STEP: Partial<Record<RepositoryStateEnum, IndexingStepId>> = {
  UPLOADED: 'scanning',
  QUEUED: 'scanning',
  SCANNING: 'scanning',
  PARSING: 'parsing',
  INDEXING: 'indexing',
  EMBEDDING: 'embedding',
  ANALYZING: 'analyzing',
  READY: 'ready',
  REINDEXING: 'indexing',
  STALE: 'analyzing',
  FAILED: 'indexing',
  CANCELLED: 'indexing',
};

function stepIndex(id: IndexingStepId): number {
  return STEP_ORDER.indexOf(id);
}

function resolveActiveStep(
  index: IndexResponse | null,
  repositoryState: RepositoryStateResponse | null,
  createInFlight: boolean
): IndexingStepId {
  if (index?.status === 'READY' || repositoryState?.state === 'READY') {
    return 'ready';
  }
  if (index?.status === 'FAILED' || repositoryState?.state === 'FAILED') {
    return STATE_TO_STEP[repositoryState?.state ?? 'FAILED'] ?? 'indexing';
  }
  if (repositoryState?.state) {
    return STATE_TO_STEP[repositoryState.state] ?? (createInFlight ? 'indexing' : 'scanning');
  }
  if (index?.status === 'INDEXING' || createInFlight) {
    return 'indexing';
  }
  return 'scanning';
}

export function buildIndexingSteps(
  index: IndexResponse | null,
  repositoryState: RepositoryStateResponse | null,
  createInFlight: boolean
): IndexingStep[] {
  const failed = index?.status === 'FAILED' || repositoryState?.state === 'FAILED';
  const active = resolveActiveStep(index, repositoryState, createInFlight);
  const activeIdx = stepIndex(active);

  return STEP_ORDER.map((id, idx) => {
    let status: StepUiStatus = 'pending';
    if (failed && id === active) {
      status = 'error';
    } else if (active === 'ready') {
      status = 'complete';
    } else if (idx < activeIdx) {
      status = 'complete';
    } else if (idx === activeIdx) {
      status = 'active';
    }
    return { id, label: STEP_LABELS[id], status };
  });
}

export function resolveProgress(
  index: IndexResponse | null,
  repositoryState: RepositoryStateResponse | null,
  createInFlight: boolean
): number {
  if (index?.status === 'READY' || repositoryState?.state === 'READY') return 100;
  if (repositoryState && typeof repositoryState.progress === 'number') {
    return repositoryState.progress;
  }
  if (createInFlight || index?.status === 'INDEXING') return 10;
  if (index?.status === 'NOT_INDEXED') return 0;
  return 0;
}

export function resolveCurrentStage(
  index: IndexResponse | null,
  repositoryState: RepositoryStateResponse | null,
  createInFlight: boolean
): string {
  if (repositoryState?.current_stage) return repositoryState.current_stage;
  if (index?.status === 'READY') return 'Indexing complete';
  if (index?.status === 'FAILED') return 'Indexing failed';
  if (createInFlight || index?.status === 'INDEXING') return 'Building repository index';
  if (repositoryState?.state) return repositoryState.state;
  return 'Waiting to start';
}

export function adaptIndexingSnapshot(params: {
  uploadId: string;
  index: IndexResponse | null;
  repositoryState: RepositoryStateResponse | null;
  createInFlight: boolean;
  createErrorMessage?: string | null;
  events?: IndexingSnapshot['events'];
}): IndexingSnapshot {
  const { uploadId, index, repositoryState, createInFlight, createErrorMessage, events = [] } =
    params;

  const failed =
    Boolean(createErrorMessage) ||
    index?.status === 'FAILED' ||
    repositoryState?.state === 'FAILED' ||
    repositoryState?.state === 'CANCELLED';
  const isReady = index?.status === 'READY' || repositoryState?.state === 'READY';
  
  // Determine if actually processing (vs just loading initial state)
  const isProcessing = 
    createInFlight ||
    index?.status === 'INDEXING' ||
    ['SCANNING', 'PARSING', 'INDEXING', 'EMBEDDING', 'ANALYZING'].includes(repositoryState?.state || '');

  // Build detailed failure reason
  let failureReason: string | null = null;
  if (failed) {
    if (createErrorMessage) {
      failureReason = createErrorMessage;
    } else if (repositoryState?.failure_reason) {
      failureReason = repositoryState.failure_reason;
    } else if (index?.status === 'FAILED') {
      failureReason = 'Indexing failed';
    } else if (!repositoryState && !index) {
      failureReason = 'Repository not found - it may have been deleted or the upload failed';
    } else if (repositoryState?.state === 'FAILED') {
      failureReason = `Indexing failed: ${repositoryState.state}`;
    } else if (repositoryState?.state === 'CANCELLED') {
      failureReason = 'Indexing was cancelled';
    }
  }

  return {
    uploadId,
    index,
    repositoryState,
    steps: buildIndexingSteps(index, repositoryState, createInFlight),
    events,
    progress: resolveProgress(index, repositoryState, createInFlight),
    currentStage: resolveCurrentStage(index, repositoryState, createInFlight),
    clientStatus: failed ? 'error' : isReady ? 'success' : isProcessing ? 'processing' : 'loading',
    failureReason,
    isReady,
  };
}

/** Prefer index READY for product readiness; fall back to repository-state READY. */
export function isRepositoryReady(
  index: IndexResponse | null,
  repositoryState: RepositoryStateResponse | null
): boolean {
  return index?.status === 'READY' || repositoryState?.state === 'READY';
}
