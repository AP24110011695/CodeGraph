import { SeverityBadge } from '@/features/_shared';
import type { CodeSmell } from '../api/quality.types';

interface Hotspot {
  file: string;
  smellCount: number;
  maxSeverity: string;
  smells: CodeSmell[];
}

interface HotspotsListProps {
  smells: CodeSmell[];
}

function severityRank(severity: string): number {
  const value = severity.toLowerCase();
  if (value.includes('critical')) return 4;
  if (value.includes('major') || value.includes('high')) return 3;
  if (value.includes('medium')) return 2;
  return 1;
}

function buildHotspots(smells: CodeSmell[]): Hotspot[] {
  const byFile = new Map<string, CodeSmell[]>();

  for (const smell of smells) {
    const isHotspot =
      severityRank(smell.severity) >= 3 ||
      smell.severity.toLowerCase().includes('critical') ||
      smell.severity.toLowerCase().includes('major');
    if (!isHotspot) continue;

    const existing = byFile.get(smell.file) ?? [];
    existing.push(smell);
    byFile.set(smell.file, existing);
  }

  if (byFile.size === 0) {
    for (const smell of smells) {
      const existing = byFile.get(smell.file) ?? [];
      existing.push(smell);
      byFile.set(smell.file, existing);
    }
  }

  return [...byFile.entries()]
    .map(([file, fileSmells]) => {
      const sorted = [...fileSmells].sort(
        (a, b) => severityRank(b.severity) - severityRank(a.severity)
      );
      return {
        file,
        smellCount: fileSmells.length,
        maxSeverity: sorted[0]?.severity ?? 'minor',
        smells: sorted,
      };
    })
    .sort((a, b) => b.smellCount - a.smellCount || severityRank(b.maxSeverity) - severityRank(a.maxSeverity));
}

export function HotspotsList({ smells }: HotspotsListProps) {
  const hotspots = buildHotspots(smells);

  if (hotspots.length === 0) {
    return (
      <div className="rounded-md border border-border-base bg-bg-elevated p-4">
        <h3 className="text-sm font-medium text-text-primary">Hotspots</h3>
        <p className="mt-2 text-sm text-text-secondary">No high-severity smell hotspots detected.</p>
      </div>
    );
  }

  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <h3 className="mb-3 text-sm font-medium text-text-primary">Hotspots</h3>
      <div className="space-y-3">
        {hotspots.slice(0, 12).map((hotspot) => (
          <div
            key={hotspot.file}
            className="rounded-md border border-border-base bg-bg-base p-3"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-xs font-medium text-text-primary">{hotspot.file}</p>
              <div className="flex items-center gap-2">
                <SeverityBadge severity={hotspot.maxSeverity} />
                <span className="text-[11px] text-text-tertiary">
                  {hotspot.smellCount} smell{hotspot.smellCount === 1 ? '' : 's'}
                </span>
              </div>
            </div>
            <ul className="mt-2 space-y-1 text-xs text-text-secondary">
              {hotspot.smells.slice(0, 3).map((smell, index) => (
                <li key={`${smell.type}-${smell.line ?? index}`}>
                  {smell.type}
                  {smell.line != null ? ` (line ${smell.line})` : ''}: {smell.description}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
