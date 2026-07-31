import { X } from 'lucide-react';
import { Button } from '@/design-system/primitives/Button';
import { Badge } from '@/design-system/primitives/Badge';
import { Separator } from '@/design-system/primitives/Separator';
import type { KnowledgeGraphNodeModel } from '../api/knowledge-graph.types';

interface EntityDetailPanelProps {
  node: KnowledgeGraphNodeModel | null;
  resolveName: (id: string) => string;
  onClose: () => void;
  onSelectRelated: (id: string) => void;
}

export function EntityDetailPanel({
  node,
  resolveName,
  onClose,
  onSelectRelated,
}: EntityDetailPanelProps) {
  if (!node) return null;

  const propertyEntries = Object.entries(node.properties);

  return (
    <aside className="flex h-full w-80 shrink-0 flex-col border-l border-border-base bg-bg-elevated">
      <div className="flex items-start justify-between gap-2 border-b border-border-base p-4">
        <div className="min-w-0">
          <h2 className="truncate text-sm font-medium text-text-primary">{node.name}</h2>
          <p className="mt-1 text-xs text-text-tertiary">{node.type}</p>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose} aria-label="Close detail panel">
          <X className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {node.labels.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {node.labels.map((label) => (
              <Badge key={label} variant="default">
                {label}
              </Badge>
            ))}
          </div>
        )}

        <div className="grid grid-cols-2 gap-2">
          <MetaStat label="Outgoing" value={node.outgoingCount} />
          <MetaStat label="Incoming" value={node.incomingCount} />
        </div>

        <Separator />

        <RelatedList
          title="Outgoing"
          ids={node.outgoing}
          resolveName={resolveName}
          onSelect={onSelectRelated}
          empty="No outgoing relationships"
        />

        <RelatedList
          title="Incoming"
          ids={node.incoming}
          resolveName={resolveName}
          onSelect={onSelectRelated}
          empty="No incoming relationships"
        />

        {propertyEntries.length > 0 && (
          <>
            <Separator />
            <div>
              <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-text-tertiary">
                Properties
              </h3>
              <dl className="space-y-1 text-xs text-text-secondary">
                {propertyEntries.map(([key, value]) => (
                  <div key={key} className="flex justify-between gap-2">
                    <dt className="shrink-0">{key}</dt>
                    <dd className="truncate text-right text-text-primary">
                      {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </dd>
                  </div>
                ))}
              </dl>
            </div>
          </>
        )}
      </div>
    </aside>
  );
}

function MetaStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-border-base bg-bg-base p-2">
      <p className="text-[10px] uppercase tracking-wide text-text-tertiary">{label}</p>
      <p className="text-lg font-medium text-text-primary">{value}</p>
    </div>
  );
}

function RelatedList({
  title,
  ids,
  resolveName,
  onSelect,
  empty,
}: {
  title: string;
  ids: string[];
  resolveName: (id: string) => string;
  onSelect: (id: string) => void;
  empty: string;
}) {
  return (
    <div>
      <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-text-tertiary">
        {title}
      </h3>
      {ids.length === 0 ? (
        <p className="text-xs text-text-tertiary">{empty}</p>
      ) : (
        <ul className="space-y-1">
          {ids.map((id) => (
            <li key={id}>
              <button
                type="button"
                className="w-full truncate rounded-md px-2 py-1.5 text-left text-xs text-text-secondary hover:bg-bg-subtle hover:text-text-primary"
                onClick={() => onSelect(id)}
              >
                {resolveName(id)}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
