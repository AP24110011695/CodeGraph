import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/design-system/primitives/Button';
import {
  AnalysisEmptyState,
  AnalysisErrorState,
  AnalysisLoadingState,
  AnalysisPageShell,
} from '@/features/_shared';
import { useNotificationStore } from '@/core/store/notification.store';
import { isAPIError } from '@/core/api/errors';
import { useGenerateReportMutation, useReportsListQuery, useReportSummaryQuery } from '../api/reports.queries';
import type { EngineeringReportDto, ReportType } from '../api/reports.types';
import { ReportCard } from './ReportCard';
import { ReportViewer } from './ReportViewer';

interface ReportsPanelProps {
  repoId: string;
  reportId?: string;
}

const REPORT_TYPES: ReportType[] = [
  'executive',
  'architecture',
  'technical_debt',
  'repository_health',
  'security_overview',
];

export function ReportsPanel({ repoId, reportId }: ReportsPanelProps) {
  const navigate = useNavigate();
  const [reportType, setReportType] = useState<ReportType>('executive');
  const [cachedReport, setCachedReport] = useState<EngineeringReportDto | null>(null);
  const listQuery = useReportsListQuery(repoId);
  const summaryQuery = useReportSummaryQuery(repoId);
  const generateMutation = useGenerateReportMutation(repoId);
  const addNotification = useNotificationStore((s) => s.addNotification);

  useEffect(() => {
    setCachedReport(null);
  }, [repoId]);

  const selected = useMemo(() => {
    const fromList =
      listQuery.data?.reports?.find((report) => report.report_id === reportId) ?? null;
    if (fromList) return fromList;
    if (cachedReport && cachedReport.report_id === reportId) return cachedReport;
    if (generateMutation.data?.report_id === reportId) return generateMutation.data;
    return null;
  }, [cachedReport, generateMutation.data, listQuery.data?.reports, reportId]);

  const onGenerate = async () => {
    try {
      const report = await generateMutation.mutateAsync({
        report_type: reportType,
        export_format: 'markdown',
      });
      setCachedReport(report);
      addNotification({
        title: 'Report generated',
        description: report.title,
        tone: 'success',
      });
      navigate(`/dashboard/${repoId}/reports/${report.report_id}`);
    } catch (error) {
      addNotification({
        title: 'Report generation failed',
        description: isAPIError(error) ? error.message : 'Unknown error',
        tone: 'danger',
      });
    }
  };

  if (reportId) {
    if (listQuery.isLoading || (listQuery.isFetching && !selected)) {
      return (
        <AnalysisPageShell title="Report">
          <AnalysisLoadingState />
        </AnalysisPageShell>
      );
    }
    if (listQuery.isError && !selected) {
      return (
        <AnalysisPageShell title="Report">
          <AnalysisErrorState error={listQuery.error} onRetry={() => void listQuery.refetch()} />
        </AnalysisPageShell>
      );
    }
    if (!selected) {
      return (
        <AnalysisPageShell
          title="Report"
          actions={
            <Button variant="secondary" size="sm" onClick={() => navigate(`/dashboard/${repoId}/reports`)}>
              Back to list
            </Button>
          }
        >
          <AnalysisEmptyState
            title="Report not found"
            description="Generate a new report or return to the reports list."
            action={
              <Button variant="secondary" size="sm" onClick={() => navigate(`/dashboard/${repoId}/reports`)}>
                Back to list
              </Button>
            }
          />
        </AnalysisPageShell>
      );
    }
    return (
      <AnalysisPageShell
        title={selected.title || 'Report'}
        description={`Type: ${selected.report_type}`}
        actions={
          <Button variant="secondary" size="sm" onClick={() => navigate(`/dashboard/${repoId}/reports`)}>
            Back to list
          </Button>
        }
        className="overflow-hidden"
      >
        <div className="-m-6">
          <ReportViewer report={selected} />
        </div>
      </AnalysisPageShell>
    );
  }

  return (
    <AnalysisPageShell
      title="Reports"
      description="Engineering intelligence reports composed from repository analysis modules."
      actions={
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={reportType}
            onChange={(event) => setReportType(event.target.value as ReportType)}
            className="h-8 rounded-md border border-border-base bg-bg-elevated px-2 text-xs text-text-primary"
            aria-label="Report type"
          >
            {REPORT_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
          <Button
            variant="primary"
            size="sm"
            disabled={generateMutation.isPending}
            onClick={() => void onGenerate()}
          >
            {generateMutation.isPending ? 'Generating…' : 'Generate report'}
          </Button>
        </div>
      }
    >
      {summaryQuery.isError && (
        <p className="mb-4 text-xs text-text-tertiary">
          Report summary unavailable. List data below may still be usable.
        </p>
      )}
      {summaryQuery.data && (
        <div className="mb-4 flex flex-wrap gap-2">
          <BadgeStat label="Reports" value={String(summaryQuery.data.report_count ?? 0)} />
          <BadgeStat
            label="Health"
            value={`${Number(summaryQuery.data.health_score ?? 0).toFixed(0)} (${summaryQuery.data.health_grade ?? '—'})`}
          />
        </div>
      )}

      {listQuery.isLoading && <AnalysisLoadingState />}
      {listQuery.isError && (
        <AnalysisErrorState error={listQuery.error} onRetry={() => void listQuery.refetch()} />
      )}
      {listQuery.isSuccess && ((listQuery.data.reports ?? []).length === 0 ? (
        <AnalysisEmptyState
          title="No reports yet"
          description="Generate an executive or architecture report to get started."
        />
      ) : (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {(listQuery.data.reports ?? []).map((report) => (
            <ReportCard key={report.report_id} report={report} repoId={repoId} />
          ))}
        </div>
      ))}
    </AnalysisPageShell>
  );
}

function BadgeStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border-base bg-bg-elevated px-3 py-2 text-xs">
      <span className="text-text-tertiary">{label}: </span>
      <span className="text-text-primary">{value}</span>
    </div>
  );
}
