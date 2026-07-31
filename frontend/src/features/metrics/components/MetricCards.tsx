import type { MetricsResponse } from '../api/metrics.types';
import { formatBytes } from '../api/metrics.adapters';

interface MetricCardsProps {
  metrics: MetricsResponse;
}

export function MetricCards({ metrics }: MetricCardsProps) {
  const { summary, statistics, quality, security, architecture, smells } = metrics;

  const cards = [
    { label: 'Files', value: String(summary.total_files) },
    { label: 'Directories', value: String(summary.total_directories) },
    { label: 'Total size', value: formatBytes(summary.total_size) },
    { label: 'Lines of code', value: statistics.code_lines?.toLocaleString() ?? '—' },
    { label: 'Quality score', value: quality.quality_score?.toString() ?? '—' },
    { label: 'Security score', value: security.security_score?.toString() ?? '—' },
    { label: 'Modules', value: String(architecture.modules) },
    { label: 'Code smells', value: String(smells.smell_count) },
  ];

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="rounded-md border border-border-base bg-bg-elevated px-3 py-2"
        >
          <p className="text-[11px] uppercase tracking-wide text-text-tertiary">{card.label}</p>
          <p className="text-lg font-medium text-text-primary">{card.value}</p>
        </div>
      ))}
    </div>
  );
}
