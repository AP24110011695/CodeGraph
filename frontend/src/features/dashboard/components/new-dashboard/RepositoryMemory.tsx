import { Skeleton } from '@/design-system/primitives/Skeleton';
import { 
  BrainCircuit, 
  FileText, 
  Database, 
  Zap,
  Target
} from 'lucide-react';

interface RepositoryMemoryProps {
  knowledgeGraphSize?: number;
  semanticChunks?: number;
  indexedFiles?: number;
  embeddings?: number;
  aiReadiness?: number;
  coverage?: number;
  loading?: boolean;
}

export function RepositoryMemory({
  knowledgeGraphSize,
  semanticChunks,
  indexedFiles,
  embeddings,
  aiReadiness,
  coverage,
  loading = false,
}: RepositoryMemoryProps) {
  if (loading) {
    return (
      <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm">
        <div className="mb-4">
          <Skeleton className="h-5 w-32" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      </div>
    );
  }

  const metrics = [
    {
      icon: BrainCircuit,
      label: 'Knowledge Graph',
      value: knowledgeGraphSize?.toLocaleString() || 'N/A',
      color: 'text-accent-default',
    },
    {
      icon: FileText,
      label: 'Semantic Chunks',
      value: semanticChunks?.toLocaleString() || 'N/A',
      color: 'text-info',
    },
    {
      icon: Database,
      label: 'Indexed Files',
      value: indexedFiles?.toLocaleString() || 'N/A',
      color: 'text-success',
    },
    {
      icon: Zap,
      label: 'Embeddings',
      value: embeddings?.toLocaleString() || 'N/A',
      color: 'text-warning',
    },
    {
      icon: Target,
      label: 'AI Readiness',
      value: aiReadiness !== undefined ? `${aiReadiness}%` : 'N/A',
      color: 'text-accent-default',
    },
  ];

  const coverageValue = coverage !== undefined ? `${coverage}%` : 'N/A';

  return (
    <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm transition-all hover:shadow-md">
      <div className="mb-4 flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-bg-base/50">
          <BrainCircuit className="h-4 w-4 text-text-secondary" />
        </div>
        <h3 className="text-sm font-semibold text-text-primary">Repository Memory</h3>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <div
              key={metric.label}
              className="flex flex-col items-center gap-2 rounded-xl border border-border-base/50 bg-bg-base/50 p-3 transition-all hover:border-border-base hover:bg-bg-base"
            >
              <div className={`flex h-8 w-8 items-center justify-center rounded-lg bg-bg-elevated/50 ${metric.color}`}>
                <Icon className="h-4 w-4" />
              </div>
              <div className="text-center">
                <p className="text-[10px] text-text-tertiary">{metric.label}</p>
                <p className="text-xs font-semibold text-text-primary">{metric.value}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 rounded-lg bg-bg-base/50 p-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-text-tertiary">Coverage</span>
          <span className="text-xs font-semibold text-text-primary">{coverageValue}</span>
        </div>
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-bg-elevated">
          <div
            className="h-full rounded-full bg-accent-default transition-all duration-500"
            style={{ width: coverage !== undefined ? `${coverage}%` : '0%' }}
          />
        </div>
      </div>
    </div>
  );
}
