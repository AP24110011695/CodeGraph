import { Badge } from '@/design-system/primitives/Badge';
import type { SnapshotComparison } from '../api/timeline.types';
import { SnapshotCard } from './SnapshotCard';

interface ComparisonViewProps {
  comparison: SnapshotComparison;
}

export function ComparisonView({ comparison }: ComparisonViewProps) {
  return (
    <div className="space-y-4">
      <div className="rounded-md border border-border-base bg-bg-elevated p-4">
        <h3 className="text-sm font-medium text-text-primary">Change summary</h3>
        <p className="mt-2 text-sm text-text-secondary">{comparison.changeSummary}</p>
        {comparison.moduleDelta.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {comparison.moduleDelta.map((item) => (
              <Badge key={item} variant={item.startsWith('+') ? 'success' : 'warning'}>
                {item}
              </Badge>
            ))}
          </div>
        )}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <SnapshotCard snapshot={comparison.left} title="Earlier" />
        <SnapshotCard snapshot={comparison.right} title="Later" />
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <FileList title="Only later" files={comparison.addedFiles} />
        <FileList title="Only earlier" files={comparison.removedFiles} />
        <FileList title="Overlap" files={comparison.sharedFiles} />
      </div>
    </div>
  );
}

function FileList({ title, files }: { title: string; files: string[] }) {
  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-3">
      <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-text-tertiary">
        {title} ({files.length})
      </h4>
      {files.length === 0 ? (
        <p className="text-xs text-text-tertiary">None</p>
      ) : (
        <ul className="max-h-40 space-y-1 overflow-auto text-xs text-text-secondary">
          {files.slice(0, 40).map((file) => (
            <li key={file} className="truncate font-mono">
              {file}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
