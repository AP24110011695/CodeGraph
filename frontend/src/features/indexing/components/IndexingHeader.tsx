import { Badge } from '@/design-system/primitives/Badge';
import { FolderGit2 } from 'lucide-react';

interface IndexingHeaderProps {
  repositoryName: string;
  progress: number;
  currentStage: string;
  status: 'loading' | 'success' | 'error' | 'processing';
}

export function IndexingHeader({
  repositoryName,
  progress,
  currentStage,
  status,
}: IndexingHeaderProps) {
  const badgeVariant =
    status === 'success' ? 'success' : status === 'error' ? 'danger' : status === 'processing' ? 'accent' : 'default';

  return (
    <div className="rounded-2xl border border-border-base bg-[#181614] p-6 shadow-xl space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-border-base bg-[#121110] text-accent-default shadow-inner">
            <FolderGit2 className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl font-semibold text-text-primary tracking-tight">{repositoryName}</h1>
              <Badge variant={badgeVariant} className="uppercase font-semibold text-[10px] tracking-wider">
                {status}
              </Badge>
            </div>
            <p className="text-xs text-text-secondary mt-0.5">{currentStage}</p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-2xl font-bold text-accent-default">{progress}%</span>
          <p className="text-[11px] text-text-tertiary">Indexed</p>
        </div>
      </div>

      <div className="space-y-1.5">
        <div className="relative h-2 overflow-hidden rounded-full bg-[#121110] border border-border-base">
          <div
            className="h-full rounded-full bg-gradient-to-r from-accent-default to-accent-hover transition-all duration-normal shadow-sm"
            style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
          />
        </div>
      </div>
      
      <p className="text-[11px] text-text-tertiary">
        Real-time indexing status polled from analysis pipeline. Please keep this browser open.
      </p>
    </div>
  );
}
