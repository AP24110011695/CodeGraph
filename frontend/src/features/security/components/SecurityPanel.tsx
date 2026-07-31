import {
  AnalysisEmptyState,
  AnalysisErrorState,
  AnalysisLoadingState,
  AnalysisPageShell,
} from '@/features/_shared';
import { useSecurityQuery } from '../api/security.queries';
import { RemediationPanel } from './RemediationPanel';
import { SecurityFindings } from './SecurityFindings';
import { VulnerabilityList } from './VulnerabilityList';

interface SecurityPanelProps {
  repoId: string;
}

export function SecurityPanel({ repoId }: SecurityPanelProps) {
  const securityQuery = useSecurityQuery(repoId);

  if (securityQuery.isLoading) {
    return (
      <AnalysisPageShell title="Security">
        <AnalysisLoadingState rows={5} />
      </AnalysisPageShell>
    );
  }

  if (securityQuery.isError) {
    return (
      <AnalysisPageShell title="Security">
        <AnalysisErrorState
          error={securityQuery.error}
          onRetry={() => void securityQuery.refetch()}
        />
      </AnalysisPageShell>
    );
  }

  if (!securityQuery.data) {
    return (
      <AnalysisPageShell title="Security">
        <AnalysisEmptyState
          title="No security data"
          description="Security analysis could not be loaded for this repository."
        />
      </AnalysisPageShell>
    );
  }

  const { summary, issues, total_issues } = securityQuery.data;

  return (
    <AnalysisPageShell
      title="Security"
      description="Static security analysis findings and remediation guidance."
    >
      <div className="space-y-4">
        <SecurityFindings summary={summary} totalIssues={total_issues} />
        <VulnerabilityList issues={issues} />
        <RemediationPanel issues={issues} />
      </div>
    </AnalysisPageShell>
  );
}
