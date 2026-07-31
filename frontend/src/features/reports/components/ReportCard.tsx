import { Link } from 'react-router-dom';
import { FileText } from 'lucide-react';
import { Badge } from '@/design-system/primitives/Badge';
import { formatDate, formatRelative } from '@/lib/format';
import type { EngineeringReportDto } from '../api/reports.types';

interface ReportCardProps {
  report: EngineeringReportDto;
  repoId: string;
}

export function ReportCard({ report, repoId }: ReportCardProps) {
  const healthGrade = report.repository_health_score?.grade;

  return (
    <Link
      to={`/dashboard/${repoId}/reports/${report.report_id}`}
      className="block rounded-md border border-border-base bg-bg-elevated p-4 transition-colors duration-fast hover:border-border-strong"
    >
      <div className="mb-3 flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-accent-default" aria-hidden />
          <h3 className="text-sm font-medium text-text-primary">{report.title || 'Untitled report'}</h3>
        </div>
        <Badge variant="accent">{report.report_type}</Badge>
      </div>
      <p className="line-clamp-2 text-xs text-text-secondary">
        {report.executive_summary || report.ai_engineering_summary || 'Engineering report'}
      </p>
      <div className="mt-3 flex flex-wrap items-center gap-2 text-[11px] text-text-tertiary">
        {healthGrade && (
          <>
            <span>Health {healthGrade}</span>
            <span>·</span>
          </>
        )}
        {report.generated_at && (
          <>
            <span>{formatDate(report.generated_at)}</span>
            <span>·</span>
            <span>{formatRelative(report.generated_at)}</span>
          </>
        )}
      </div>
    </Link>
  );
}
