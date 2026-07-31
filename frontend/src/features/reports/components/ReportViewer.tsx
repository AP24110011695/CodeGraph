import { MarkdownContent } from '@/features/_shared';
import type { EngineeringReportDto } from '../api/reports.types';
import { ReportMetaSidebar } from './ReportMetaSidebar';

interface ReportViewerProps {
  report: EngineeringReportDto;
}

export function ReportViewer({ report }: ReportViewerProps) {
  const sections = report.sections ?? [];
  const markdown =
    report.exported_content ||
    [
      `# ${report.title || 'Report'}`,
      report.executive_summary && `## Executive summary\n\n${report.executive_summary}`,
      report.architecture_summary && `## Architecture\n\n${report.architecture_summary}`,
      report.risk_assessment && `## Risk assessment\n\n${report.risk_assessment}`,
      report.technical_debt_summary && `## Technical debt\n\n${report.technical_debt_summary}`,
      report.ai_engineering_summary && `## AI summary\n\n${report.ai_engineering_summary}`,
      ...sections.map(
        (section) =>
          `## ${section.title}\n\n${section.content}${
            (section.highlights ?? []).length
              ? `\n\n${(section.highlights ?? []).map((h) => `- ${h}`).join('\n')}`
              : ''
          }`
      ),
    ]
      .filter(Boolean)
      .join('\n\n');

  return (
    <div className="flex min-h-[480px] flex-col lg:flex-row">
      <div className="min-w-0 flex-1 overflow-auto p-6">
        <MarkdownContent content={markdown || '_No report content available._'} />
      </div>
      <ReportMetaSidebar report={report} />
    </div>
  );
}
