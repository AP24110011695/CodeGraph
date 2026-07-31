import type { QualityRecommendations } from '../api/quality.types';

interface RecommendationsListProps {
  recommendations: QualityRecommendations;
}

function ListSection({
  title,
  items,
  emptyText,
}: {
  title: string;
  items: string[];
  emptyText: string;
}) {
  return (
    <div>
      <h4 className="text-xs font-medium uppercase tracking-wide text-text-tertiary">{title}</h4>
      {items.length === 0 ? (
        <p className="mt-2 text-sm text-text-secondary">{emptyText}</p>
      ) : (
        <ul className="mt-2 space-y-1 text-sm text-text-secondary">
          {items.map((item) => (
            <li key={item}>• {item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function RecommendationsList({ recommendations }: RecommendationsListProps) {
  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <h3 className="mb-4 text-sm font-medium text-text-primary">Recommendations</h3>
      <div className="grid gap-4 md:grid-cols-3">
        <ListSection
          title="Strengths"
          items={recommendations.strengths}
          emptyText="No strengths identified."
        />
        <ListSection
          title="Weaknesses"
          items={recommendations.weaknesses}
          emptyText="No weaknesses identified."
        />
        <ListSection
          title="Actions"
          items={recommendations.recommendations}
          emptyText="No recommendations available."
        />
      </div>
    </div>
  );
}
