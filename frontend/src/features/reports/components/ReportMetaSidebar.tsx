import { Badge } from '@/design-system/primitives/Badge';
import { formatDate } from '@/lib/format';
import type { EngineeringReportDto } from '../api/reports.types';

interface ReportMetaSidebarProps {
  report: EngineeringReportDto;
}

export function ReportMetaSidebar({ report }: ReportMetaSidebarProps) {
  return (
    <aside className="w-72 shrink-0 space-y-4 border-l border-border-base bg-bg-elevated p-4">
      <div>
        <h2 className="text-sm font-medium text-text-primary">Metadata</h2>
        <p className="mt-1 text-xs text-text-tertiary">Report details and sources</p>
      </div>
      <dl className="space-y-2 text-xs text-text-secondary">
        <MetaRow label="Type" value={report.report_type} />
        <MetaRow label="Generated" value={formatDate(report.generated_at)} />
        <MetaRow label="Confidence" value={`${Math.round(report.confidence_score * 100)}%`} />
        <MetaRow
          label="Health"
          value={`${report.repository_health_score.overall.toFixed(0)} (${report.repository_health_score.grade})`}
        />
        <MetaRow label="Format" value={report.export_format} />
      </dl>
      {report.sources_used.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-text-tertiary">
            Sources
          </p>
          <div className="flex flex-wrap gap-1">
            {report.sources_used.map((source) => (
              <Badge key={source} variant="default">
                {source}
              </Badge>
            ))}
          </div>
        </div>
      )}
      {report.improvement_recommendations.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-text-tertiary">
            Top recommendations
          </p>
          <ul className="space-y-1 text-xs text-text-secondary">
            {report.improvement_recommendations.slice(0, 5).map((item) => (
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
