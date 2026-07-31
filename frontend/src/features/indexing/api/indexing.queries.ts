import { useEffect, useMemo, useRef, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { isAPIError } from '@/core/api/errors';
import { useRepositoryStore } from '@/core/store/repository.store';
import { adaptIndexingSnapshot, isRepositoryReady } from './indexing.adapters';
import { createIndex, getIndexStatus, getRepositoryState } from './indexing.api';
import type { IndexingEvent, IndexResponse, RepositoryStateResponse } from './indexing.types';

export const indexingKeys = {
  all: ['indexing'] as const,
  index: (uploadId: string) => ['indexing', 'index', uploadId] as const,
  state: (uploadId: string) => ['indexing', 'state', uploadId] as const,
};

function pushEvent(
  previous: IndexingEvent[],
  message: string,
  level: IndexingEvent['level'] = 'info'
): IndexingEvent[] {
  const last = previous[previous.length - 1];
  if (last?.message === message) return previous;
  return [
    ...previous,
    {
      id: crypto.randomUUID(),
      at: new Date().toISOString(),
      level,
      message,
    },
  ].slice(-80);
}

export function useIndexingStatusQuery(uploadId: string, enabled = true) {
  return useQuery({
    queryKey: indexingKeys.index(uploadId),
    queryFn: () => getIndexStatus(uploadId),
    enabled: Boolean(uploadId) && enabled,
    refetchInterval: (query) => {
      if (query.state.error) return false;
      const status = query.state.data?.status;
      if (status === 'READY' || status === 'FAILED') return false;
      return 2000;
    },
    retry: (failureCount, error) => {
      if (isAPIError(error) && (error.status === 404 || error.status === 400)) return false;
      return failureCount < 2;
    },
  });
}

export function useRepositoryStateQuery(uploadId: string, enabled = true) {
  return useQuery({
    queryKey: indexingKeys.state(uploadId),
    queryFn: () => getRepositoryState(uploadId),
    enabled: Boolean(uploadId) && enabled,
    refetchInterval: (query) => {
      if (query.state.error) return false;
      const state = query.state.data?.state;
      if (state === 'READY' || state === 'FAILED' || state === 'CANCELLED') return false;
      return 2000;
    },
    retry: (failureCount, error) => {
      if (isAPIError(error) && error.status === 404) return false;
      return failureCount < 2;
    },
  });
}

export function useStartIndexingMutation(uploadId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ['indexing', 'create', uploadId],
    mutationFn: () => createIndex(uploadId),
    onSuccess: (data) => {
      queryClient.setQueryData(indexingKeys.index(uploadId), data);
      void queryClient.invalidateQueries({ queryKey: indexingKeys.state(uploadId) });
    },
  });
}

/**
 * Orchestrates POST /index + polling GET /index and GET /repository-state.
 * SSE is intentionally not used (backend does not expose it).
 */
export function useIndexingOrchestrator(uploadId: string) {
  const applyIndexingSnapshot = useRepositoryStore((s) => s.applyIndexingSnapshot);
  const setIndexingStatus = useRepositoryStore((s) => s.setIndexingStatus);

  const [events, setEvents] = useState<IndexingEvent[]>([]);
  const startedRef = useRef(false);

  const indexQuery = useIndexingStatusQuery(uploadId);
  const stateQuery = useRepositoryStateQuery(uploadId);
  const startMutation = useStartIndexingMutation(uploadId);

  useEffect(() => {
    startedRef.current = false;
    setEvents([]);
  }, [uploadId]);

  useEffect(() => {
    if (!uploadId || startedRef.current) return;
    if (indexQuery.isLoading) return;

    const status = indexQuery.data?.status;
    if (status === 'READY') {
      startedRef.current = true;
      setEvents((prev) => pushEvent(prev, 'Index already ready', 'success'));
      return;
    }

    if (status === 'INDEXING' || startMutation.isPending || startMutation.isSuccess) {
      startedRef.current = true;
      return;
    }

    startedRef.current = true;
    setEvents((prev) => pushEvent(prev, 'Starting indexing pipeline'));
    setIndexingStatus('indexing');
    startMutation.mutate(undefined, {
      onSuccess: () => {
        setEvents((prev) => pushEvent(prev, 'Indexing request completed', 'success'));
      },
      onError: (error) => {
        const message = isAPIError(error) ? error.message : 'Failed to start indexing';
        // 409 = already exists / in progress — keep polling.
        if (isAPIError(error) && error.status === 409) {
          setEvents((prev) => pushEvent(prev, message, 'warning'));
          return;
        }
        setEvents((prev) => pushEvent(prev, message, 'error'));
        setIndexingStatus('error');
      },
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps -- start once per uploadId when index query settles
  }, [uploadId, indexQuery.isLoading, indexQuery.data?.status]);

  const indexStatus = indexQuery.data?.status;
  const indexData = indexQuery.data;
  const repoState = stateQuery.data?.state;
  const repoStage = stateQuery.data?.current_stage;
  const repoProgress = stateQuery.data?.progress;
  const repositoryStateData = stateQuery.data;

  useEffect(() => {
    if (!indexData) return;
    setEvents((prev) =>
      pushEvent(
        prev,
        `Index status: ${indexData.status}`,
        indexData.status === 'READY' ? 'success' : 'info'
      )
    );
  }, [indexStatus, indexData]);

  useEffect(() => {
    if (!repositoryStateData) return;
    const stage = repositoryStateData.current_stage || repositoryStateData.state;
    setEvents((prev) => pushEvent(prev, `Repository state: ${stage}`));
  }, [repoState, repoStage, repoProgress, repositoryStateData]);

  const createErrorMessage =
    startMutation.isError && !(isAPIError(startMutation.error) && startMutation.error.status === 409)
      ? isAPIError(startMutation.error)
        ? startMutation.error.message
        : 'Indexing failed'
      : indexQuery.isError
        ? isAPIError(indexQuery.error)
          ? indexQuery.error.message
          : 'Failed to load index status'
        : null;

  const snapshot = useMemo(() => {
    const index = (indexQuery.data ?? null) as IndexResponse | null;
    const repositoryState = (stateQuery.data ?? null) as RepositoryStateResponse | null;
    return adaptIndexingSnapshot({
      uploadId,
      index,
      repositoryState,
      createInFlight: startMutation.isPending,
      createErrorMessage,
      events,
    });
  }, [
    uploadId,
    indexQuery.data,
    stateQuery.data,
    startMutation.isPending,
    createErrorMessage,
    events,
  ]);

  useEffect(() => {
    applyIndexingSnapshot({
      indexingStatus: snapshot.isReady
        ? 'ready'
        : snapshot.clientStatus === 'error'
          ? 'error'
          : 'indexing',
      backendState: snapshot.repositoryState?.state ?? null,
      indexStatus: snapshot.index?.status ?? null,
      progress: snapshot.progress,
      currentStage: snapshot.currentStage,
      failureReason: snapshot.failureReason,
    });
  }, [snapshot, applyIndexingSnapshot]);

  const retry = () => {
    startedRef.current = true;
    setEvents((prev) => pushEvent(prev, 'Retrying indexing…', 'warning'));
    setIndexingStatus('indexing');
    startMutation.mutate(undefined, {
      onSuccess: (data) => {
        setEvents((prev) => pushEvent(prev, 'Retry succeeded', 'success'));
        void indexQuery.refetch();
        void stateQuery.refetch();
        return data;
      },
      onError: (error) => {
        const message = isAPIError(error) ? error.message : 'Retry failed';
        setEvents((prev) => pushEvent(prev, message, 'error'));
        setIndexingStatus('error');
      },
    });
  };

  return {
    snapshot,
    isLoading: indexQuery.isLoading && !indexQuery.data,
    isReady: isRepositoryReady(snapshot.index, snapshot.repositoryState),
    retry,
    refetch: () => {
      void indexQuery.refetch();
      void stateQuery.refetch();
    },
  };
}
