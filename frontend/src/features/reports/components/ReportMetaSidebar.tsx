import { Badge } from '@/design-system/primitives/Badge';
import { formatDate } from '@/lib/format';
import type { EngineeringReportDto } from '../api/reports.types';

interface ReportMetaSidebarProps {
  report: EngineeringReportDto;
}

export function ReportMetaSidebar({ report }: ReportMetaSidebarProps) {
  const health = report.repository_health_score;
  const sources = report.sources_used ?? [];
  const recommendations = report.improvement_recommendations ?? [];
  const confidence = typeof report.confidence_score === 'number' ? report.confidence_score : null;

  return (
    <aside className="w-full shrink-0 space-y-4 border-t border-border-base bg-bg-elevated p-4 lg:w-72 lg:border-l lg:border-t-0">
      <div>
        <h2 className="text-sm font-medium text-text-primary">Metadata</h2>
        <p className="mt-1 text-xs text-text-tertiary">Report details and sources</p>
      </div>
      <dl className="space-y-2 text-xs text-text-secondary">
        <MetaRow label="Type" value={report.report_type || '—'} />
        <MetaRow
          label="Generated"
          value={report.generated_at ? formatDate(report.generated_at) : '—'}
        />
        <MetaRow
          label="Confidence"
          value={confidence !== null ? `${Math.round(confidence * 100)}%` : '—'}
        />
        <MetaRow
          label="Health"
          value={
            health
              ? `${Number(health.overall ?? 0).toFixed(0)} (${health.grade ?? '—'})`
              : '—'
          }
        />
        <MetaRow label="Format" value={report.export_format || '—'} />
      </dl>
      {sources.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-text-tertiary">
            Sources
          </p>
          <div className="flex flex-wrap gap-1">
            {sources.map((source) => (
              <Badge key={source} variant="default">
                {source}
              </Badge>
            ))}
          </div>
        </div>
      )}
      {recommendations.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-text-tertiary">
            Top recommendations
          </p>
          <ul className="space-y-1 text-xs text-text-secondary">
            {recommendations.slice(0, 5).map((item) => (
              <li key={item} className="rounded-md bg-bg-base px-2 py-1.5">
                {item}
              </li>
            ))}
          </ul>
        </div>
      )}
    </aside>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-2">
      <dt>{label}</dt>
      <dd className="text-right text-text-primary">{value}</dd>
    </div>
  );
}
