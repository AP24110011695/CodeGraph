import { useEffect, useMemo } from 'react';
import { Skeleton } from '@/design-system/primitives/Skeleton';
import {
  AnalysisEmptyState,
  AnalysisErrorState,
} from '@/features/_shared';
import { useArchitectureQuery } from '../api/architecture.queries';
import { useArchitectureStore } from '../store/architecture.store';
import { ArchitectureCanvas } from './ArchitectureCanvas';
import { ArchitectureLayers } from './ArchitectureLayers';
import { ExplanationPanel } from './ExplanationPanel';

interface ArchitecturePanelProps {
  repoId: string;
}

export function ArchitecturePanel({ repoId }: ArchitecturePanelProps) {
  const selectedModuleName = useArchitectureStore((s) => s.selectedModuleName);
  const resetArchitecture = useArchitectureStore((s) => s.reset);
  const architectureQuery = useArchitectureQuery(repoId);

  useEffect(() => {
    resetArchitecture();
  }, [repoId, resetArchitecture]);

  const layerCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const mod of architectureQuery.data?.modules ?? []) {
      counts[mod.layer] = (counts[mod.layer] ?? 0) + 1;
    }
    return counts;
  }, [architectureQuery.data?.modules]);

  if (architectureQuery.isLoading) {
    return (
      <div className="flex h-[calc(100vh-3rem)] min-h-[480px]">
        <div className="flex flex-1 flex-col">
          <Skeleton className="h-10 w-full rounded-none" />
          <div className="flex-1 p-4">
            <div className="grid h-full grid-cols-3 gap-3">
              {Array.from({ length: 9 }).map((_, index) => (
                <Skeleton key={index} className="h-20 w-full" />
              ))}
            </div>
          </div>
        </div>
        <Skeleton className="h-full w-80 rounded-none" />
      </div>
    );
  }

  if (architectureQuery.isError) {
    return (
      <AnalysisErrorState
        error={architectureQuery.error}
        onRetry={() => void architectureQuery.refetch()}
      />
    );
  }

  const data = architectureQuery.data;
  if (!data || data.modules.length === 0) {
    return (
      <AnalysisEmptyState
        title="No architecture modules detected"
        description="Upload and index a repository to analyze its layered architecture."
      />
    );
  }

  return (
    <div className="flex h-[calc(100vh-3rem)] min-h-[480px]">
      <div className="flex min-w-0 flex-1 flex-col">
        <ArchitectureLayers layers={data.layers} moduleCounts={layerCounts} />
        <div className="min-h-0 flex-1">
          <ArchitectureCanvas modules={data.modules} edges={data.edges} layers={data.layers} />
        </div>
      </div>
      <ExplanationPanel repositoryId={repoId} selectedModuleName={selectedModuleName} />
    </div>
  );
}
