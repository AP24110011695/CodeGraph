import { Search, Command } from 'lucide-react';
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
    <div className="space-y-4">
      <form
        className="flex items-center gap-3"
        onSubmit={(event) => {
          event.preventDefault();
          commitQuery();
        }}
      >
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
          <Input
            value={draftQuery}
            onChange={(event) => setDraftQuery(event.target.value)}
            placeholder="Find authentication handlers, entry points, risky modules…"
            className="h-12 rounded-2xl border-border-base bg-[#121110] pl-11 pr-16 text-sm shadow-inner transition-all focus:border-accent-default focus:ring-2 focus:ring-accent-default/30"
            aria-label="Semantic search"
            data-search-input
          />
          <div className="pointer-events-none absolute right-4 top-1/2 flex -translate-y-1/2 items-center gap-1 rounded-md border border-border-base bg-[#181614] px-2 py-0.5 text-[10px] font-medium text-text-tertiary">
            <Command className="h-3 w-3" />
            <span>K</span>
          </div>
        </div>
        <Button type="submit" variant="primary" size="lg">
          Search
        </Button>
      </form>

      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs text-text-tertiary mr-1 font-medium">Mode:</span>
        {MODES.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setMode(item)}
            className={
              mode === item
                ? 'rounded-full border border-accent-muted/40 bg-accent-subtle px-3 py-1 text-xs font-semibold text-accent-default shadow-sm transition-all'
                : 'rounded-full border border-border-base bg-[#181614] px-3 py-1 text-xs font-medium text-text-tertiary hover:border-border-strong hover:text-text-secondary transition-all'
            }
          >
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}

