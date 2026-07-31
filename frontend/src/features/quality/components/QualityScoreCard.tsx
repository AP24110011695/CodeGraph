import type { QualityScores } from '../api/quality.types';

interface QualityScoreCardProps {
  projectName: string;
  scores: QualityScores;
}

const SCORE_LABELS: Array<{ key: keyof QualityScores; label: string }> = [
  { key: 'architecture', label: 'Architecture' },
  { key: 'security', label: 'Security' },
  { key: 'documentation', label: 'Documentation' },
  { key: 'maintainability', label: 'Maintainability' },
  { key: 'testing', label: 'Testing' },
  { key: 'complexity', label: 'Complexity' },
  { key: 'readability', label: 'Readability' },
  { key: 'scalability', label: 'Scalability' },
];

function scoreColor(value: number): string {
  if (value >= 75) return 'bg-success';
  if (value >= 50) return 'bg-warning';
  return 'bg-danger';
}

function overallScore(scores: QualityScores): number {
  const values = Object.values(scores);
  return Math.round(values.reduce((sum, value) => sum + value, 0) / values.length);
}

export function QualityScoreCard({ projectName, scores }: QualityScoreCardProps) {
  const overall = overallScore(scores);

  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-medium text-text-primary">{projectName}</h3>
          <p className="mt-1 text-xs text-text-secondary">Quality dimension scores (0–100)</p>
        </div>
        <div className="text-right">
          <p className="text-[11px] uppercase tracking-wide text-text-tertiary">Overall</p>
          <p className="text-2xl font-medium text-text-primary">{overall}</p>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        {SCORE_LABELS.map(({ key, label }) => {
          const value = scores[key];
          return (
            <div key={key}>
              <div className="mb-1 flex items-center justify-between text-xs">
                <span className="text-text-secondary">{label}</span>
                <span className="font-medium text-text-primary">{value}</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-bg-subtle">
                <div
                  className={`h-full rounded-full transition-all ${scoreColor(value)}`}
                  style={{ width: `${value}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
