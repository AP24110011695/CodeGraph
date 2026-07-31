import { SeverityBadge } from '@/features/_shared';
import type { CodeSmell } from '../api/quality.types';

interface CodeSmellsListProps {
  smells: CodeSmell[];
  summary?: {
    total_smells: number;
    critical: number;
    major: number;
    minor: number;
  };
  technicalDebt?: string;
  estimatedEffort?: string;
}

export function CodeSmellsList({
  smells,
  summary,
  technicalDebt,
  estimatedEffort,
}: CodeSmellsListProps) {
  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <div className="mb-3 flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 className="text-sm font-medium text-text-primary">Code smells</h3>
          {summary && (
            <p className="mt-1 text-xs text-text-secondary">
              {summary.total_smells} total · {summary.critical} critical · {summary.major} major ·{' '}
              {summary.minor} minor
            </p>
          )}
        </div>
        {(technicalDebt || estimatedEffort) && (
          <div className="text-right text-xs text-text-secondary">
            {technicalDebt && <p>Debt: {technicalDebt}</p>}
            {estimatedEffort && <p>Effort: {estimatedEffort}</p>}
          </div>
        )}
      </div>

      {smells.length === 0 ? (
        <p className="text-sm text-text-secondary">No code smells detected.</p>
      ) : (
        <div className="max-h-[420px] space-y-2 overflow-auto">
          {smells.map((smell, index) => (
            <div
              key={`${smell.file}-${smell.type}-${smell.line ?? index}`}
              className="rounded-md border border-border-base bg-bg-base p-3"
            >
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-medium text-text-primary">{smell.type}</span>
                <SeverityBadge severity={smell.severity} />
                <span className="text-[11px] text-text-tertiary">
                  {smell.file}
                  {smell.line != null ? `:${smell.line}` : ''}
                </span>
              </div>
              <p className="mt-2 text-xs text-text-secondary">{smell.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
