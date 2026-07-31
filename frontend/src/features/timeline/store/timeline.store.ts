import { create } from 'zustand';

interface TimelineUiState {
  selectedSha: string | null;
  compareLeftSha: string | null;
  compareRightSha: string | null;
  comparisonMode: boolean;
  setSelectedSha: (sha: string | null) => void;
  setCompareLeftSha: (sha: string | null) => void;
  setCompareRightSha: (sha: string | null) => void;
  setComparisonMode: (value: boolean) => void;
  clearComparison: () => void;
}

export const useTimelineStore = create<TimelineUiState>((set) => ({
  selectedSha: null,
  compareLeftSha: null,
  compareRightSha: null,
  comparisonMode: false,
  setSelectedSha: (sha) => set({ selectedSha: sha }),
  setCompareLeftSha: (sha) => set({ compareLeftSha: sha }),
  setCompareRightSha: (sha) => set({ compareRightSha: sha }),
  setComparisonMode: (value) => set({ comparisonMode: value }),
  clearComparison: () =>
    set({ compareLeftSha: null, compareRightSha: null, comparisonMode: false }),
}));
