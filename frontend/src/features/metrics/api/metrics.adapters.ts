import type { MetricsArchitecture, MetricsStatistics } from './metrics.types';

export interface ChartDatum {
  name: string;
  value: number;
  percentage?: number;
}

export const CHART_COLORS = [
  '#7C3AED',
  '#3B82F6',
  '#22C55E',
  '#F59E0B',
  '#EF4444',
  '#A1A1AA',
] as const;

function normalizeLanguageEntry(
  name: string,
  entry: { count: number; percentage: number } | number
): ChartDatum {
  if (typeof entry === 'number') {
    return { name, value: entry };
  }
  return {
    name,
    value: entry.count,
    percentage: entry.percentage,
  };
}

export function adaptLanguageBreakdown(statistics: MetricsStatistics): ChartDatum[] {
  const breakdown = statistics.language_breakdown;
  if (Object.keys(breakdown).length > 0) {
    return Object.entries(breakdown)
      .map(([name, entry]) => normalizeLanguageEntry(name, entry))
      .sort((a, b) => b.value - a.value);
  }

  const supported = statistics.supported_languages;
  const total = Object.values(supported).reduce((sum, count) => sum + count, 0);
  return Object.entries(supported)
    .map(([name, count]) => ({
      name,
      value: count,
      percentage: total > 0 ? Math.round((count / total) * 10000) / 100 : 0,
    }))
    .sort((a, b) => b.value - a.value);
}

export function adaptComplexityBreakdown(
  statistics: MetricsStatistics,
  architecture: MetricsArchitecture
): ChartDatum[] {
  const quality = statistics.quality_breakdown;
  if (Object.keys(quality).length > 0) {
    return Object.entries(quality)
      .map(([name, value]) => ({
        name: name.replace(/_/g, ' '),
        value,
      }))
      .sort((a, b) => b.value - a.value);
  }

  return [
    { name: 'Modules', value: architecture.modules },
    { name: 'Components', value: architecture.components },
    { name: 'Relationships', value: architecture.relationships },
    { name: 'Functions', value: statistics.total_functions },
    { name: 'Classes', value: statistics.total_classes },
  ].filter((item) => item.value > 0);
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
