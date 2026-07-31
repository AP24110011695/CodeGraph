import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { generateReport, getReportSummary, listReports } from './reports.api';
import type { ReportGenerateRequest } from './reports.types';

export const reportsKeys = {
  all: ['reports'] as const,
  list: (repoId: string) => ['reports', 'list', repoId] as const,
  summary: (repoId: string) => ['reports', 'summary', repoId] as const,
};

export function useReportsListQuery(repoId: string) {
  return useQuery({
    queryKey: reportsKeys.list(repoId),
    queryFn: () => listReports(repoId),
    enabled: Boolean(repoId),
    staleTime: 60_000,
  });
}

export function useReportSummaryQuery(repoId: string) {
  return useQuery({
    queryKey: reportsKeys.summary(repoId),
    queryFn: () => getReportSummary(repoId),
    enabled: Boolean(repoId),
    staleTime: 60_000,
  });
}

export function useGenerateReportMutation(repoId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request?: ReportGenerateRequest) => generateReport(repoId, request),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: reportsKeys.list(repoId) });
      void queryClient.invalidateQueries({ queryKey: reportsKeys.summary(repoId) });
    },
  });
}
