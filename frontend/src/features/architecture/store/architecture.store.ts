import { create } from 'zustand';

interface ArchitectureUiState {
  selectedModuleName: string | null;
  explainQuery: string;
  setSelectedModuleName: (name: string | null) => void;
  setExplainQuery: (query: string) => void;
  reset: () => void;
}

export const useArchitectureStore = create<ArchitectureUiState>((set) => ({
  selectedModuleName: null,
  explainQuery: '',
  setSelectedModuleName: (selectedModuleName) => set({ selectedModuleName }),
  setExplainQuery: (explainQuery) => set({ explainQuery }),
  reset: () => set({ selectedModuleName: null, explainQuery: '' }),
}));
