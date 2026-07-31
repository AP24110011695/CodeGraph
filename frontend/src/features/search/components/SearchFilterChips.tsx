import { Badge } from '@/design-system/primitives/Badge';
import { useSearchStore } from '../store/search.store';

interface SearchFilterChipsProps {
  languages: string[];
}

export function SearchFilterChips({ languages }: SearchFilterChipsProps) {
  const filters = useSearchStore((s) => s.filters);
  const toggleLanguage = useSearchStore((s) => s.toggleLanguage);
  const setMinScore = useSearchStore((s) => s.setMinScore);
  const resetFilters = useSearchStore((s) => s.resetFilters);

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-xs text-text-tertiary">Filters</span>
      {languages.map((language) => {
        const active = filters.languages.includes(language);
        return (
          <button key={language} type="button" onClick={() => toggleLanguage(language)}>
            <Badge variant={active ? 'accent' : 'default'}>{language}</Badge>
          </button>
        );
      })}
      <label className="ml-2 flex items-center gap-2 text-xs text-text-secondary">
        Min score
        <input
          type="range"
          min={0}
          max={1}
          step={0.05}
          value={filters.minScore}
          onChange={(event) => setMinScore(Number(event.target.value))}
          className="accent-accent-default"
        />
        <span className="w-8 text-text-tertiary">{filters.minScore.toFixed(2)}</span>
      </label>
      {(filters.languages.length > 0 || filters.minScore > 0) && (
        <button
          type="button"
          className="text-xs text-accent-default hover:underline"
          onClick={resetFilters}
        >
          Reset
        </button>
      )}
    </div>
  );
}
