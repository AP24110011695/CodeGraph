import type { SearchResultModel } from '../api/search.types';

interface CodePreviewPanelProps {
  result: SearchResultModel | null;
}

/**
 * Lightweight code preview.
 * Monaco is deferred — architecture allows a styled <pre> until Monaco is wired.
 */
export function CodePreviewPanel({ result }: CodePreviewPanelProps) {
  if (!result) {
    return (
      <div className="flex h-full items-center justify-center p-6 text-sm text-text-secondary">
        Select a result to preview the matched snippet.
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border-base px-4 py-3">
        <h2 className="truncate text-sm font-medium text-text-primary">{result.path}</h2>
        <p className="text-xs text-text-tertiary">
          {result.language} · lines {result.lineStart}–{result.lineEnd} · relevance{' '}
          {(result.score * 100).toFixed(0)}%
        </p>
      </div>
      <div className="flex-1 overflow-auto p-4">
        <pre className="overflow-x-auto rounded-md border border-border-base bg-bg-base p-4 font-mono text-[12px] leading-6 text-text-primary">
          <code>{result.snippet}</code>
        </pre>
      </div>
    </div>
  );
}
