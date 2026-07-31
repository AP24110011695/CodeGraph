import { Badge } from '@/design-system/primitives/Badge';
import { cn } from '@/lib/cn';
import type { SearchResultModel } from '../api/search.types';

interface SearchResultItemProps {
  result: SearchResultModel;
  selected?: boolean;
  onSelect: () => void;
}

export function SearchResultItem({ result, selected, onSelect }: SearchResultItemProps) {
  const scorePercent = Math.round(Math.min(1, Math.max(0, result.score)) * 100);

  return (
    <button
      type="button"
      onClick={onSelect}
      className={cn(
        'w-full rounded-md border px-3 py-3 text-left transition-colors duration-fast',
        selected
          ? 'border-accent-default bg-accent-subtle'
          : 'border-border-base bg-bg-elevated hover:border-border-strong'
      )}
    >
      <div className="mb-2 flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="truncate text-sm text-text-primary">{result.path}</p>
          <p className="text-xs text-text-tertiary">
            Lines {result.lineStart}–{result.lineEnd}
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-1">
          <Badge variant="default">{result.language}</Badge>
          <Badge variant="info">{scorePercent}%</Badge>
        </div>
      </div>
      <pre className="overflow-x-auto rounded-md bg-bg-base p-2 font-mono text-[11px] leading-5 text-text-secondary">
        {result.snippet}
      </pre>
      {typeof result.contextScore === 'number' && (
        <p className="mt-2 text-[11px] text-text-tertiary">
          Context score: {result.contextScore.toFixed(3)}
        </p>
      )}
    </button>
  );
}
