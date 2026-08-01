import { Skeleton } from '@/design-system/primitives/Skeleton';
import { 
  File, 
  Folder, 
  Code2, 
  Box, 
  Layers, 
  GitBranch, 
  Database, 
  Package, 
  Server, 
  Route
} from 'lucide-react';

interface SnapshotData {
  files?: number;
  directories?: number;
  functions?: number;
  classes?: number;
  interfaces?: number;
  components?: number;
  hooks?: number;
  models?: number;
  services?: number;
  routes?: number;
  controllers?: number;
  apis?: number;
  databaseModels?: number;
  dependencies?: number;
}

interface RepositorySnapshotProps {
  data?: SnapshotData;
  loading?: boolean;
}

const SNAPSHOT_ITEMS = [
  { key: 'files', label: 'Files', icon: File },
  { key: 'directories', label: 'Directories', icon: Folder },
  { key: 'functions', label: 'Functions', icon: Code2 },
  { key: 'classes', label: 'Classes', icon: Box },
  { key: 'interfaces', label: 'Interfaces', icon: Layers },
  { key: 'components', label: 'Components', icon: Box },
  { key: 'hooks', label: 'Hooks', icon: GitBranch },
  { key: 'models', label: 'Models', icon: Database },
  { key: 'services', label: 'Services', icon: Server },
  { key: 'routes', label: 'Routes', icon: Route },
  { key: 'controllers', label: 'Controllers', icon: Server },
  { key: 'apis', label: 'APIs', icon: Route },
  { key: 'databaseModels', label: 'Database Models', icon: Database },
  { key: 'dependencies', label: 'Dependencies', icon: Package },
];

export function RepositorySnapshot({ data, loading = false }: RepositorySnapshotProps) {
  if (loading) {
    return (
      <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm">
        <h3 className="mb-4 text-sm font-semibold text-text-primary">Repository Snapshot</h3>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {SNAPSHOT_ITEMS.map((item) => (
            <Skeleton key={item.key} className="h-16 w-full" />
          ))}
        </div>
      </div>
    );
  }

  const availableItems = SNAPSHOT_ITEMS.filter(
    (item) => data && data[item.key as keyof SnapshotData] !== undefined
  );

  if (availableItems.length === 0) {
    return (
      <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm">
        <h3 className="mb-4 text-sm font-semibold text-text-primary">Repository Snapshot</h3>
        <p className="text-sm text-text-tertiary">No snapshot data available</p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm transition-all hover:shadow-md">
      <h3 className="mb-4 text-sm font-semibold text-text-primary">Repository Snapshot</h3>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        {availableItems.map((item) => {
          const Icon = item.icon;
          const value = data?.[item.key as keyof SnapshotData];
          return (
            <div
              key={item.key}
              className="flex items-center gap-3 rounded-xl border border-border-base/50 bg-bg-base/50 p-3 transition-all hover:border-border-base hover:bg-bg-base"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-bg-elevated/50">
                <Icon className="h-4 w-4 text-text-secondary" />
              </div>
              <div className="min-w-0">
                <p className="text-xs text-text-tertiary">{item.label}</p>
                <p className="text-sm font-semibold text-text-primary">
                  {value !== undefined ? value.toLocaleString() : 'N/A'}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
