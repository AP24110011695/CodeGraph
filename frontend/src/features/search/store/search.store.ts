import { create } from 'zustand';
import type { SearchMode, SearchUiFilters } from '../api/search.types';

interface SearchUiState {
  draftQuery: string;
  committedQuery: string;
  mode: SearchMode;
  filters: SearchUiFilters;
  selectedResultId: string | null;
  setDraftQuery: (value: string) => void;
  commitQuery: (value?: string) => void;
  setMode: (mode: SearchMode) => void;
  toggleLanguage: (language: string) => void;
  setMinScore: (value: number) => void;
  setSelectedResultId: (id: string | null) => void;
  resetFilters: () => void;
}

export const useSearchStore = create<SearchUiState>((set, get) => ({
  draftQuery: '',
  committedQuery: '',
  mode: 'hybrid',
  filters: {
    languages: [],
    minScore: 0,
  },
  selectedResultId: null,
  setDraftQuery: (draftQuery) => set({ draftQuery }),
  commitQuery: (value) => {
    const next = (value ?? get().draftQuery).trim();
    set({ committedQuery: next, draftQuery: next, selectedResultId: null });
  },
  setMode: (mode) => set({ mode, selectedResultId: null }),
  toggleLanguage: (language) =>
    set((state) => {
      const exists = state.filters.languages.includes(language);
      return {
        filters: {
          ...state.filters,
          languages: exists
            ? state.filters.languages.filter((item) => item !== language)
            : [...state.filters.languages, language],
        },
      };
    }),
  setMinScore: (minScore) =>
    set((state) => ({ filters: { ...state.filters, minScore } })),
  setSelectedResultId: (selectedResultId) => set({ selectedResultId }),
  resetFilters: () =>
    set({
      filters: { languages: [], minScore: 0 },
      selectedResultId: null,
    }),
}));
