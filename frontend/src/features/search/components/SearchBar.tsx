import { Search } from 'lucide-react';
import { Input } from '@/design-system/primitives/Input';
import { Button } from '@/design-system/primitives/Button';
import type { SearchMode } from '../api/search.types';
import { useSearchStore } from '../store/search.store';

const MODES: SearchMode[] = ['hybrid', 'semantic', 'keyword'];

export function SearchBar() {
  const draftQuery = useSearchStore((s) => s.draftQuery);
  const mode = useSearchStore((s) => s.mode);
  const setDraftQuery = useSearchStore((s) => s.setDraftQuery);
  const commitQuery = useSearchStore((s) => s.commitQuery);
  const setMode = useSearchStore((s) => s.setMode);

  return (
    <div className="space-y-3">
      <form
        className="flex items-center gap-2"
        onSubmit={(event) => {
          event.preventDefault();
          commitQuery();
        }}
      >
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
          <Input
            value={draftQuery}
            onChange={(event) => setDraftQuery(event.target.value)}
            placeholder="Find authentication handlers, entry points, risky modules…"
            className="h-10 pl-9"
            aria-label="Semantic search"
          />
        </div>
        <Button type="submit" variant="primary">
          Search
        </Button>
      </form>

      <div className="flex flex-wrap gap-2">
        {MODES.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setMode(item)}
            className={
              mode === item
                ? 'rounded-md border border-accent-muted/40 bg-accent-subtle px-2 py-1 text-xs text-accent-default'
                : 'rounded-md border border-border-base px-2 py-1 text-xs text-text-tertiary hover:text-text-secondary'
            }
          >
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}
