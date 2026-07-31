import { create } from 'zustand';

interface ImpactUiState {
  target: string;
  targetType: string;
  changeType: string;
  setTarget: (value: string) => void;
  setTargetType: (value: string) => void;
  setChangeType: (value: string) => void;
  reset: () => void;
}

const initialState = {
  target: '',
  targetType: 'auto',
  changeType: 'modify',
};

export const useImpactStore = create<ImpactUiState>((set) => ({
  ...initialState,
  setTarget: (value) => set({ target: value }),
  setTargetType: (value) => set({ targetType: value }),
  setChangeType: (value) => set({ changeType: value }),
  reset: () => set(initialState),
}));
