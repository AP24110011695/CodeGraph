import { Skeleton } from '@/design-system/primitives/Skeleton';
import { 
  GitCommit, 
  FileEdit, 
  AlertTriangle,
  Layers
} from 'lucide-react';

interface ActivityItem {
  type: 'commit' | 'file_change' | 'risk' | 'module';
  title: string;
  description: string;
  timestamp: string;
  metadata?: {
    filesChanged?: number;
    riskLevel?: string;
    modulesAffected?: string[];
  };
}

interface RecentActivityTimelineProps {
  activities?: ActivityItem[];
  loading?: boolean;
}

const ACTIVITY_ICONS = {
  commit: GitCommit,
  file_change: FileEdit,
  risk: AlertTriangle,
  module: Layers,
};

const ACTIVITY_COLORS = {
  commit: 'text-success bg-success/10 border-success/20',
  file_change: 'text-info bg-info/10 border-info/20',
  risk: 'text-danger bg-danger/10 border-danger/20',
  module: 'text-accent-default bg-accent-subtle border-accent-muted/30',
};

export function RecentActivityTimeline({ activities, loading = false }: RecentActivityTimelineProps) {
  if (loading) {
    return (
      <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm">
        <h3 className="mb-4 text-sm font-semibold text-text-primary">Recent Activity</h3>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      </div>
    );
  }

  if (!activities || activities.length === 0) {
    return (
      <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm">
        <h3 className="mb-4 text-sm font-semibold text-text-primary">Recent Activity</h3>
        <p className="text-sm text-text-tertiary">No recent activity</p>
      </div>
    );
  }

  const displayActivities = activities.slice(0, 5);

  return (
    <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm transition-all hover:shadow-md">
      <h3 className="mb-4 text-sm font-semibold text-text-primary">Recent Activity</h3>
      <div className="space-y-4">
        {displayActivities.map((activity, index) => {
          const Icon = ACTIVITY_ICONS[activity.type];
          const colorClass = ACTIVITY_COLORS[activity.type];
          return (
            <div
              key={index}
              className="group flex gap-3 rounded-xl border border-border-base/50 bg-bg-base/50 p-3 transition-all hover:border-border-base hover:bg-bg-base"
            >
              <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border ${colorClass}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium text-text-primary">{activity.title}</p>
                  <span className="text-[10px] text-text-tertiary whitespace-nowrap">{activity.timestamp}</span>
                </div>
                <p className="mt-0.5 text-xs text-text-secondary line-clamp-2">{activity.description}</p>
                {activity.metadata && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {activity.metadata.filesChanged !== undefined && (
                      <span className="text-[10px] text-text-tertiary">
                        {activity.metadata.filesChanged} files changed
                      </span>
                    )}
                    {activity.metadata.riskLevel && (
                      <span className="text-[10px] text-danger">
                        {activity.metadata.riskLevel} risk
                      </span>
                    )}
                    {activity.metadata.modulesAffected && activity.metadata.modulesAffected.length > 0 && (
                      <span className="text-[10px] text-text-tertiary">
                        {activity.metadata.modulesAffected.length} modules
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
