import { SeverityBadge } from '@/features/_shared';
import type { ChangeRiskResult, ImpactStatistics } from '../api/impact.types';

interface RiskSummaryProps {
  risk: ChangeRiskResult;
  statistics: ImpactStatistics;
  impactSummary: string;
  whatBreaks: string[];
}

export function RiskSummary({ risk, statistics, impactSummary, whatBreaks }: RiskSummaryProps) {
  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-medium text-text-primary">Risk summary</h3>
          {impactSummary && (
            <p className="mt-2 text-sm text-text-secondary">{impactSummary}</p>
          )}
        </div>
        <div className="text-right">
          <SeverityBadge severity={risk.risk_level} />
          <p className="mt-1 text-2xl font-medium text-text-primary">
            {risk.risk_score.toFixed(0)}
          </p>
          <p className="text-[11px] text-text-tertiary">Risk score</p>
        </div>
      </div>

      <div className="mb-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Stat label="Affected nodes" value={String(statistics.affected_nodes)} />
        <Stat label="Propagation paths" value={String(statistics.propagation_paths)} />
        <Stat label="Max depth" value={String(statistics.max_propagation_depth)} />
        <Stat
          label="Confidence"
          value={`${(statistics.confidence_score * 100).toFixed(0)}%`}
        />
      </div>

      {risk.recommendation && (
        <p className="mb-3 text-sm text-text-secondary">{risk.recommendation}</p>
      )}

      {risk.factors.length > 0 && (
        <div className="mb-3">
          <h4 className="text-xs font-medium uppercase tracking-wide text-text-tertiary">
            Risk factors
          </h4>
          <ul className="mt-2 space-y-1 text-xs text-text-secondary">
            {risk.factors.map((factor) => (
              <li key={factor}>• {factor}</li>
            ))}
          </ul>
        </div>
      )}

      {whatBreaks.length > 0 && (
        <div>
          <h4 className="text-xs font-medium uppercase tracking-wide text-text-tertiary">
            What may break
          </h4>
          <ul className="mt-2 space-y-1 text-xs text-text-secondary">
            {whatBreaks.map((item) => (
              <li key={item}>• {item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border-base bg-bg-base px-3 py-2">
      <p className="text-[11px] uppercase tracking-wide text-text-tertiary">{label}</p>
      <p className="text-lg font-medium text-text-primary">{value}</p>
    </div>
  );
}
