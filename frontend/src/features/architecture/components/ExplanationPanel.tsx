import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { Button } from '@/design-system/primitives/Button';
import { Input } from '@/design-system/primitives/Input';
import { Badge } from '@/design-system/primitives/Badge';
import { Separator } from '@/design-system/primitives/Separator';
import { Skeleton } from '@/design-system/primitives/Skeleton';
import type { ArchitectureExplanationResponse } from '../api/architecture.types';
import {
  useArchitectureExplainMutation,
  useArchitectureSummaryQuery,
} from '../api/architecture.queries';
import { useArchitectureStore } from '../store/architecture.store';

interface ExplanationPanelProps {
  repositoryId: string;
  selectedModuleName: string | null;
}

export function ExplanationPanel({ repositoryId, selectedModuleName }: ExplanationPanelProps) {
  const explainQuery = useArchitectureStore((s) => s.explainQuery);
  const setExplainQuery = useArchitectureStore((s) => s.setExplainQuery);
  const summaryQuery = useArchitectureSummaryQuery(repositoryId);
  const explainMutation = useArchitectureExplainMutation(repositoryId);
  const [explanation, setExplanation] = useState<ArchitectureExplanationResponse | null>(null);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const query = explainQuery.trim();
    if (!query) return;
    try {
      const result = await explainMutation.mutateAsync(query);
      setExplanation(result);
    } catch {
      // Error surface via explainMutation.isError below.
    }
  };

  return (
    <aside className="flex h-full w-80 shrink-0 flex-col border-l border-border-base bg-bg-elevated">
      <div className="border-b border-border-base p-4">
        <h2 className="text-sm font-medium text-text-primary">Architecture insight</h2>
        <p className="mt-1 text-xs text-text-tertiary">
          High-level summary and AI-powered explanations
        </p>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        <section>
          <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-text-tertiary">
            Summary
          </h3>
          {summaryQuery.isLoading && <Skeleton className="h-20 w-full" />}
          {summaryQuery.isError && (
            <p className="text-xs text-text-tertiary">Summary unavailable for this repository.</p>
          )}
          {summaryQuery.data && (
            <p className="text-sm leading-relaxed text-text-secondary">
              {summaryQuery.data.overall_architecture}
            </p>
          )}
        </section>

        {selectedModuleName && (
          <>
            <Separator />
            <section>
              <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-text-tertiary">
                Selected module
              </h3>
              <Badge variant="accent">{selectedModuleName}</Badge>
            </section>
          </>
        )}

        <Separator />

        <section>
          <h3 className="mb-2 text-xs font-medium uppercase tracking-wide text-text-tertiary">
            Ask a question
          </h3>
          <form onSubmit={(event) => void onSubmit(event)} className="space-y-2">
            <Input
              value={explainQuery}
              onChange={(event) => setExplainQuery(event.target.value)}
              placeholder="e.g. How does auth flow work?"
              aria-label="Architecture question"
            />
            <Button
              type="submit"
              variant="primary"
              size="sm"
              className="w-full"
              disabled={explainMutation.isPending || !explainQuery.trim()}
            >
              {explainMutation.isPending ? (
                <>
                  <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
                  Explaining…
                </>
              ) : (
                'Explain'
              )}
            </Button>
          </form>
          {explainMutation.isError && (
            <p className="mt-2 text-xs text-danger">Failed to generate explanation.</p>
          )}
        </section>

        {explanation && (
          <section className="space-y-3">
            <Separator />
            <div>
              <div className="mb-2 flex items-center justify-between gap-2">
                <h3 className="text-xs font-medium uppercase tracking-wide text-text-tertiary">
                  Explanation
                </h3>
                <Badge variant="default">
                  {(explanation.confidence_score * 100).toFixed(0)}% confidence
                </Badge>
              </div>
              <p className="text-sm leading-relaxed text-text-secondary">{explanation.summary}</p>
            </div>

            {explanation.referenced_modules?.length ? (
              <div>
                <h4 className="mb-1 text-xs font-medium text-text-secondary">Referenced modules</h4>
                <div className="flex flex-wrap gap-1">
                  {explanation.referenced_modules.map((mod) => (
                    <Badge key={mod} variant="default">
                      {mod}
                    </Badge>
                  ))}
                </div>
              </div>
            ) : null}

            {explanation.evidence?.length ? (
              <div>
                <h4 className="mb-1 text-xs font-medium text-text-secondary">Evidence</h4>
                <ul className="list-inside list-disc space-y-1 text-xs text-text-tertiary">
                  {explanation.evidence.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            ) : null}

            {explanation.reasoning_trace?.length ? (
              <div>
                <h4 className="mb-1 text-xs font-medium text-text-secondary">Reasoning trace</h4>
                <ol className="space-y-2">
                  {explanation.reasoning_trace.map((step, index) => (
                    <li key={index} className="rounded-md border border-border-base bg-bg-base p-2">
                      <p className="text-xs font-medium text-text-primary">{step.step}</p>
                      <p className="mt-0.5 text-xs text-text-tertiary">{step.description}</p>
                    </li>
                  ))}
                </ol>
              </div>
            ) : null}          </section>
        )}
      </div>
    </aside>
  );
}
