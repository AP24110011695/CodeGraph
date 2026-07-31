import { create } from 'zustand';

export type PanelLayout = 'single' | 'split' | 'triple';
export type PreferredTheme = 'dark' | 'light';

export interface GraphFilterState {
  showExternal: boolean;
  showDevDependencies: boolean;
  depth: number | null;
}

interface UiState {
  sidebarCollapsed: boolean;
  copilotPanelOpen: boolean;
  activePanelLayout: PanelLayout;
  graphFilters: GraphFilterState;
  preferredTheme: PreferredTheme;
  setSidebarCollapsed: (value: boolean) => void;
  toggleSidebarCollapsed: () => void;
  setCopilotPanelOpen: (value: boolean) => void;
  toggleCopilotPanel: () => void;
  setActivePanelLayout: (layout: PanelLayout) => void;
  setGraphFilters: (filters: Partial<GraphFilterState>) => void;
  setPreferredTheme: (theme: PreferredTheme) => void;
}

const defaultGraphFilters: GraphFilterState = {
  showExternal: true,
  showDevDependencies: false,
  depth: null,
};

export const useUiStore = create<UiState>((set) => ({
  sidebarCollapsed: false,
  copilotPanelOpen: false,
  activePanelLayout: 'single',
  graphFilters: defaultGraphFilters,
  preferredTheme: 'dark',
  setSidebarCollapsed: (value) => set({ sidebarCollapsed: value }),
  toggleSidebarCollapsed: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setCopilotPanelOpen: (value) => set({ copilotPanelOpen: value }),
  toggleCopilotPanel: () => set((state) => ({ copilotPanelOpen: !state.copilotPanelOpen })),
  setActivePanelLayout: (layout) => set({ activePanelLayout: layout }),
  setGraphFilters: (filters) =>
    set((state) => ({ graphFilters: { ...state.graphFilters, ...filters } })),
  setPreferredTheme: (theme) => set({ preferredTheme: theme }),
}));
