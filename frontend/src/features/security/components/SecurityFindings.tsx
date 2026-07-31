import type { SecuritySummary } from '../api/security.types';

interface SecurityFindingsProps {
  summary: SecuritySummary;
  totalIssues: number;
}

const SEVERITY_ITEMS: Array<{
  key: keyof SecuritySummary;
  label: string;
  color: string;
}> = [
  { key: 'critical', label: 'Critical', color: 'text-danger' },
  { key: 'high', label: 'High', color: 'text-danger' },
  { key: 'medium', label: 'Medium', color: 'text-warning' },
  { key: 'low', label: 'Low', color: 'text-info' },
];

export function SecurityFindings({ summary, totalIssues }: SecurityFindingsProps) {
  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-medium text-text-primary">Security findings</h3>
          <p className="mt-1 text-xs text-text-secondary">Issues grouped by severity</p>
        </div>
        <div className="text-right">
          <p className="text-[11px] uppercase tracking-wide text-text-tertiary">Total</p>
          <p className="text-2xl font-medium text-text-primary">{totalIssues}</p>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {SEVERITY_ITEMS.map(({ key, label, color }) => (
          <div key={key} className="rounded-md border border-border-base bg-bg-base px-3 py-2">
            <p className="text-[11px] uppercase tracking-wide text-text-tertiary">{label}</p>
            <p className={`text-lg font-medium ${color}`}>{summary[key]}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
