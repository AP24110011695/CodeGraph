import { create } from 'zustand';
import type { GraphUiFilters } from '../api/dependency-graph.types';

interface DependencyGraphUiState {
  filters: GraphUiFilters;
  selectedNodeId: string | null;
  setSearchQuery: (query: string) => void;
  toggleLanguage: (language: string) => void;
  setHideIsolated: (value: boolean) => void;
  clearLanguageFilters: () => void;
  setSelectedNodeId: (id: string | null) => void;
  resetFilters: () => void;
}

const defaultFilters: GraphUiFilters = {
  languages: [],
  hideIsolated: false,
  searchQuery: '',
};

export const useDependencyGraphStore = create<DependencyGraphUiState>((set) => ({
  filters: defaultFilters,
  selectedNodeId: null,
  setSearchQuery: (searchQuery) =>
    set((state) => ({ filters: { ...state.filters, searchQuery } })),
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
  setHideIsolated: (hideIsolated) =>
    set((state) => ({ filters: { ...state.filters, hideIsolated } })),
  clearLanguageFilters: () =>
    set((state) => ({ filters: { ...state.filters, languages: [] } })),
  setSelectedNodeId: (selectedNodeId) => set({ selectedNodeId }),
  resetFilters: () => set({ filters: defaultFilters, selectedNodeId: null }),
}));
