import type { SecurityIssue } from '../api/security.types';

interface RemediationPanelProps {
  issues: SecurityIssue[];
}

export function RemediationPanel({ issues }: RemediationPanelProps) {
  const guidance = issues.slice(0, 8);

  if (guidance.length === 0) {
    return (
      <div className="rounded-md border border-border-base bg-bg-elevated p-4">
        <h3 className="text-sm font-medium text-text-primary">Remediation guidance</h3>
        <p className="mt-2 text-sm text-text-secondary">No remediation items required.</p>
      </div>
    );
  }

  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <h3 className="mb-3 text-sm font-medium text-text-primary">Remediation guidance</h3>
      <div className="space-y-3">
        {guidance.map((issue, index) => (
          <div
            key={`${issue.rule}-${issue.file}-${issue.line}-${index}`}
            className="rounded-md border border-border-base bg-bg-base p-3"
          >
            <p className="text-xs font-medium text-text-primary">{issue.rule}</p>
            <p className="mt-1 text-[11px] text-text-tertiary">
              {issue.file}:{issue.line}
            </p>
            <p className="mt-2 text-xs text-text-secondary">{issue.description}</p>
            <p className="mt-2 text-xs text-text-tertiary">
              Remediation: Review and address the <span className="text-text-secondary">{issue.rule}</span>{' '}
              finding in {issue.language} code.
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
