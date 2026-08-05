import { Badge } from '@/design-system/primitives/Badge';
import { Skeleton } from '@/design-system/primitives/Skeleton';
import { 
  AlertTriangle, 
  Trash2,
  GitBranch,
  FileText,
  XCircle,
  type LucideIcon
} from 'lucide-react';
import type { RiskItem } from '../../api/dashboard.types';

interface RiskSummaryPanelProps {
  risks?: RiskItem[];
  overallScore?: number | null;
  overallLevel?: string | null;
  loading?: boolean;
  error?: boolean;
}

const RISK_CATEGORIES: Record<string, { icon: LucideIcon; color: string }> = {
  'Dead Code': { icon: Trash2, color: 'text-warning' },
  'Circular Dependencies': { icon: GitBranch, color: 'text-danger' },
  'Large Files': { icon: FileText, color: 'text-warning' },
  'Unused Files': { icon: Trash2, color: 'text-text-tertiary' },
  'Broken Imports': { icon: XCircle, color: 'text-danger' },
};

export function RiskSummaryPanel({ risks, overallScore, overallLevel, loading = false, error = false }: RiskSummaryPanelProps) {
  if (error) {
    return (
      <div className="rounded-2xl border border-danger/20 bg-danger/5 backdrop-blur-sm p-5 shadow-sm min-h-[200px] flex flex-col items-center justify-center">
        <AlertTriangle className="h-8 w-8 text-danger mb-3" />
        <p className="text-sm font-medium text-danger">Risk Analysis Failed</p>
        <p className="text-xs text-danger/70 mt-1">Unable to load repository risks</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <Skeleton className="h-5 w-28" />
          <Skeleton className="h-6 w-20" />
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      </div>
    );
  }

  const getOverallBadge = (level: string | null | undefined) => {
    if (!level) return null;
    const normalized = level.toLowerCase();
    if (normalized.includes('critical')) return { variant: 'danger' as const, label: 'Critical' };
    if (normalized.includes('high')) return { variant: 'danger' as const, label: 'High' };
    if (normalized.includes('medium')) return { variant: 'warning' as const, label: 'Medium' };
    if (normalized.includes('low')) return { variant: 'info' as const, label: 'Low' };
    return { variant: 'default' as const, label: level };
  };

  const overallBadge = getOverallBadge(overallLevel);

  const categorizedRisks = risks?.reduce((acc, risk) => {
    const category = risk.category || 'Other';
    if (!acc[category]) acc[category] = [];
    acc[category].push(risk);
    return acc;
  }, {} as Record<string, RiskItem[]>) || {};

  const categoryItems = Object.entries(categorizedRisks).map(([category, items]) => {
    const categoryInfo = RISK_CATEGORIES[category] || { icon: AlertTriangle, color: 'text-text-secondary' };
    return { category, items, ...categoryInfo };
  });

  return (
    <div className="rounded-2xl border border-border-base bg-bg-elevated/50 backdrop-blur-sm p-5 shadow-sm transition-all hover:shadow-md">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">Risk Summary</h3>
        {overallBadge && (
          <Badge variant={overallBadge.variant} className="px-2.5 py-1 text-xs font-medium">
            {overallBadge.label}
            {overallScore !== null && ` · ${overallScore}`}
          </Badge>
        )}
      </div>

      {categoryItems.length === 0 ? (
        <p className="text-sm text-text-tertiary">No risks detected</p>
      ) : (
        <div className="space-y-3">
          {categoryItems.map(({ category, items, icon: Icon, color }) => (
            <div
              key={category}
              className="group flex items-center gap-3 rounded-xl border border-border-base/50 bg-bg-base/50 p-3 transition-all hover:border-border-base hover:bg-bg-base cursor-pointer"
            >
              <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-bg-elevated/50 ${color}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-medium text-text-primary">{category}</p>
                  <span className="text-xs font-semibold text-text-secondary">{items.length}</span>
                </div>
                <p className="mt-0.5 text-xs text-text-tertiary truncate">
                  {items[0]?.title || 'No description'}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
