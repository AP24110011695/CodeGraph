import { create } from 'zustand';

interface KnowledgeGraphUiState {
  selectedNodeId: string | null;
  searchQuery: string;
  typeFilter: string[];
  setSelectedNodeId: (id: string | null) => void;
  setSearchQuery: (query: string) => void;
  toggleTypeFilter: (type: string) => void;
  clearTypeFilters: () => void;
  reset: () => void;
}

export const useKnowledgeGraphStore = create<KnowledgeGraphUiState>((set) => ({
  selectedNodeId: null,
  searchQuery: '',
  typeFilter: [],
  setSelectedNodeId: (selectedNodeId) => set({ selectedNodeId }),
  setSearchQuery: (searchQuery) => set({ searchQuery }),
  toggleTypeFilter: (type) =>
    set((state) => {
      const exists = state.typeFilter.includes(type);
      return {
        typeFilter: exists
          ? state.typeFilter.filter((item) => item !== type)
          : [...state.typeFilter, type],
      };
    }),
  clearTypeFilters: () => set({ typeFilter: [] }),
  reset: () => set({ selectedNodeId: null, searchQuery: '', typeFilter: [] }),
}));
