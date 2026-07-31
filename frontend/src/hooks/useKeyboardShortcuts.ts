import { useEffect } from 'react';
import { useUiStore } from '@/core/store/ui.store';

/**
 * Global keyboard shortcuts foundation.
 * ⌘K / Ctrl+K and ⌘J / Ctrl+J handlers are wired; destinations fill in later phases.
 */
export function useKeyboardShortcuts(): void {
  const toggleCopilotPanel = useUiStore((s) => s.toggleCopilotPanel);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const meta = event.metaKey || event.ctrlKey;
      if (!meta) return;

      if (event.key.toLowerCase() === 'j') {
        event.preventDefault();
        toggleCopilotPanel();
      }
    };

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [toggleCopilotPanel]);
}
