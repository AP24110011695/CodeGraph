import { SeverityBadge } from '@/features/_shared';
import type { AffectedNode, PropagationPath } from '../api/impact.types';

interface ImpactVisualizationProps {
  directDependents: AffectedNode[];
  transitiveDependents: AffectedNode[];
  propagationPaths: PropagationPath[];
}

function NodeCard({ node }: { node: AffectedNode }) {
  const severity =
    node.impact_weight >= 0.75
      ? 'critical'
      : node.impact_weight >= 0.5
        ? 'high'
        : node.impact_weight >= 0.25
          ? 'medium'
          : 'low';

  return (
    <div className="rounded-md border border-border-base bg-bg-base p-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-medium text-text-primary">{node.name}</span>
        <SeverityBadge severity={severity} />
        <span className="text-[11px] text-text-tertiary">
          {node.node_type} · {node.distance} hop{node.distance === 1 ? '' : 's'}
        </span>
      </div>
      {node.reason && <p className="mt-2 text-xs text-text-secondary">{node.reason}</p>}
    </div>
  );
}

export function ImpactVisualization({
  directDependents,
  transitiveDependents,
  propagationPaths,
}: ImpactVisualizationProps) {
  const affectedNodes = [...directDependents, ...transitiveDependents];

  return (
    <div className="space-y-4">
      <div className="rounded-md border border-border-base bg-bg-elevated p-4">
        <h3 className="mb-3 text-sm font-medium text-text-primary">Affected nodes</h3>
        {affectedNodes.length === 0 ? (
          <p className="text-sm text-text-secondary">No affected nodes predicted.</p>
        ) : (
          <div className="grid gap-2 md:grid-cols-2">
            {affectedNodes.slice(0, 12).map((node) => (
              <NodeCard key={node.id} node={node} />
            ))}
          </div>
        )}
      </div>

      <div className="rounded-md border border-border-base bg-bg-elevated p-4">
        <h3 className="mb-3 text-sm font-medium text-text-primary">Propagation paths</h3>
        {propagationPaths.length === 0 ? (
          <p className="text-sm text-text-secondary">No propagation paths found.</p>
        ) : (
          <div className="space-y-2">
            {propagationPaths.slice(0, 8).map((path, index) => (
              <div
                key={`${path.path.join('-')}-${index}`}
                className="rounded-md border border-border-base bg-bg-base p-3"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <SeverityBadge severity={path.severity} />
                  <span className="text-[11px] text-text-tertiary">
                    {path.length} hop{path.length === 1 ? '' : 's'}
                  </span>
                </div>
                <p className="mt-2 text-xs text-text-secondary">{path.path.join(' → ')}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
