import { apiClient } from '@/core/api/client';
import type {
  EngineeringReportDto,
  EngineeringReportListDto,
  EngineeringReportSummaryDto,
  ReportGenerateRequest,
} from './reports.types';

export async function listReports(repositoryId: string): Promise<EngineeringReportListDto> {
  const { data } = await apiClient.get<EngineeringReportListDto>(`/reports/${repositoryId}`, {
    timeout: 120_000,
  });
  return data;
}

export async function getReportSummary(
  repositoryId: string
): Promise<EngineeringReportSummaryDto> {
  const { data } = await apiClient.get<EngineeringReportSummaryDto>(
    `/reports/${repositoryId}/summary`
  );
  return data;
}

export async function generateReport(
  repositoryId: string,
  request: ReportGenerateRequest = { report_type: 'executive', export_format: 'markdown' }
): Promise<EngineeringReportDto> {
  const { data } = await apiClient.post<EngineeringReportDto>(
    `/reports/generate/${repositoryId}`,
    request,
    { timeout: 180_000 }
  );
  return data;
}
