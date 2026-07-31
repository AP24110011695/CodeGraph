import { Badge } from '@/design-system/primitives/Badge';
import { Skeleton } from '@/design-system/primitives/Skeleton';
import type { CopilotContextSnapshot } from '../api/copilot.types';

interface ContextPanelProps {
  context: CopilotContextSnapshot | null;
  loading?: boolean;
}

export function ContextPanel({ context, loading }: ContextPanelProps) {
  if (loading) {
    return (
      <div className="space-y-3 p-4">
        <Skeleton className="h-4 w-28" />
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-16 w-full" />
      </div>
    );
  }

  if (!context) {
    return (
      <div className="p-4 text-sm text-text-secondary">
        Context from the latest answer will appear here — related files, modules, citations, and
        recommendations.
      </div>
    );
  }

  return (
    <div className="space-y-4 overflow-y-auto p-4">
      {context.reasoningSummary && (
        <section>
          <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-text-tertiary">
            Reasoning
          </h3>
          <p className="text-sm text-text-secondary">{context.reasoningSummary}</p>
        </section>
      )}

      <SourceGroup title="Related files" items={context.relatedFiles} />
      <SourceGroup title="Related components" items={context.relatedComponents} />
      <SourceGroup title="Modules used" items={context.modulesUsed} />
      <SourceGroup title="Tools used" items={context.toolsUsed} />
      <SourceGroup title="Citations" items={context.citations} />
      <SourceGroup title="Recommendations" items={context.recommendations} />
    </div>
  );
}

function SourceGroup({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <section>
      <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-text-tertiary">
        {title}
      </h3>
      <ul className="space-y-1">
        {items.map((item) => (
          <li
            key={`${title}-${item}`}
            className="rounded-md border border-border-base bg-bg-base px-2 py-1.5 text-xs text-text-secondary"
          >
            {item}
          </li>
        ))}
      </ul>
      <div className="mt-2">
        <Badge variant="default">{items.length}</Badge>
      </div>
    </section>
  );
}
