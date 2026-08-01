import { MarkdownContent } from '@/features/_shared';
import type { EngineeringReportDto } from '../api/reports.types';
import { ReportMetaSidebar } from './ReportMetaSidebar';

interface ReportViewerProps {
  report: EngineeringReportDto;
}

export function ReportViewer({ report }: ReportViewerProps) {
  // Use exported_content (formatted markdown) as the single source of truth
  // This is populated by the MarkdownReportExporter on the backend
  const markdown = report.exported_content || '_No report content available._';

  return (
    <div className="flex min-h-[480px] flex-col lg:flex-row">
      <div className="min-w-0 flex-1 overflow-auto p-6">
        <MarkdownContent content={markdown} />
      </div>
      <ReportMetaSidebar report={report} />
    </div>
  );
}
