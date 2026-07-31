import { Badge } from '@/design-system/primitives/Badge';
import { formatDate } from '@/lib/format';
import type { TimelineSnapshot } from '../api/timeline.types';

interface SnapshotCardProps {
  snapshot: TimelineSnapshot;
  title?: string;
}

export function SnapshotCard({ snapshot, title = 'Snapshot' }: SnapshotCardProps) {
  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <div className="mb-3 flex items-center justify-between gap-2">
        <h3 className="text-sm font-medium text-text-primary">{title}</h3>
        <Badge variant="accent">{snapshot.label}</Badge>
      </div>
      <p className="text-sm text-text-secondary">{snapshot.message}</p>
      <dl className="mt-4 grid grid-cols-2 gap-2 text-xs text-text-secondary">
        <div>
          <dt className="text-text-tertiary">Author</dt>
          <dd className="text-text-primary">{snapshot.author}</dd>
        </div>
        <div>
          <dt className="text-text-tertiary">Date</dt>
          <dd className="text-text-primary">{formatDate(snapshot.timestamp)}</dd>
        </div>
        <div>
          <dt className="text-text-tertiary">Files</dt>
          <dd className="text-text-primary">{snapshot.filesChanged}</dd>
        </div>
        <div>
          <dt className="text-text-tertiary">Lines</dt>
          <dd className="text-text-primary">
            +{snapshot.insertions} / -{snapshot.deletions}
          </dd>
        </div>
      </dl>
      {snapshot.modules.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
          {snapshot.modules.slice(0, 8).map((module) => (
            <Badge key={module} variant="default">
              {module}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}
