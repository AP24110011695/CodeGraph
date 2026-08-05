import { Badge } from '@/design-system/primitives/Badge';
import { Skeleton } from '@/design-system/primitives/Skeleton';
import { 
  Lightbulb, 
  ArrowRight,
  Clock,
  Zap
} from 'lucide-react';

interface Recommendation {
  title: string;
  priority: 'high' | 'medium' | 'low';
  estimatedImpact: string;
  estimatedEffort: string;
  affectedFiles: string[];
  description: string;
}

interface TopRecommendationsPanelProps {
  recommendations?: Recommendation[];
  loading?: boolean;
}

const PRIORITY_CONFIG = {
  high: { variant: 'danger' as const, label: 'High', color: 'text-danger bg-danger/10 border-danger/20' },
  medium: { variant: 'warning' as const, label: 'Medium', color: 'text-warning bg-warning/10 border-warning/20' },
  low: { variant: 'info' as const, label: 'Low', color: 'text-info bg-info/10 border-info/20' },
};

export function TopRecommendationsPanel({ recommendations, loading = false }: TopRecommendationsPanelProps) {
  if (loading) {
    return (
      <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <Skeleton className="h-5 w-5" />
          <Skeleton className="h-5 w-32" />
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      </div>
    );
  }

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-bg-base/50">
            <Lightbulb className="h-4 w-4 text-text-secondary" />
          </div>
          <h3 className="text-sm font-semibold text-text-primary">Top Recommendations</h3>
        </div>
        <p className="text-sm text-text-tertiary">No recommendations available</p>
      </div>
    );
  }

  const displayRecommendations = recommendations.slice(0, 5);

  return (
    <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm transition-all hover:shadow-md">
      <div className="mb-4 flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-bg-base/50">
          <Lightbulb className="h-4 w-4 text-text-secondary" />
        </div>
        <h3 className="text-sm font-semibold text-text-primary">Top Recommendations</h3>
      </div>

      <div className="space-y-3">
        {displayRecommendations.map((recommendation, index) => {
          const priorityConfig = PRIORITY_CONFIG[recommendation.priority];
          return (
            <div
              key={index}
              className="group flex gap-3 rounded-xl border border-border-base/50 bg-bg-base/50 p-4 transition-all hover:border-border-base hover:bg-bg-base cursor-pointer"
            >
              <div className="flex shrink-0 flex-col items-center gap-1">
                <Badge variant={priorityConfig.variant} className="text-xs font-medium">
                  {priorityConfig.label}
                </Badge>
                <ArrowRight className="h-4 w-4 text-text-tertiary opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-text-primary group-hover:text-accent-default transition-colors">
                  {recommendation.title}
                </p>
                <p className="mt-1 text-xs text-text-secondary line-clamp-2">{recommendation.description}</p>
                
                <div className="mt-2 flex flex-wrap gap-3">
                  <div className="flex items-center gap-1 text-[10px] text-text-tertiary">
                    <Zap className="h-3 w-3" />
                    <span>Impact: {recommendation.estimatedImpact}</span>
                  </div>
                  <div className="flex items-center gap-1 text-[10px] text-text-tertiary">
                    <Clock className="h-3 w-3" />
                    <span>Effort: {recommendation.estimatedEffort}</span>
                  </div>
                  <div className="text-[10px] text-text-tertiary">
                    {recommendation.affectedFiles.length} files
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
