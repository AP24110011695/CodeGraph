import { useEffect } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { useUiStore } from '@/core/store/ui.store';

/**
 * Global keyboard shortcuts:
 * ⌘/Ctrl+J — toggle copilot panel
 * ⌘/Ctrl+K — go to search
 * ⌘/Ctrl+B — toggle sidebar
 * Escape — close copilot panel
 */
export function useKeyboardShortcuts(): void {
  const navigate = useNavigate();
  const location = useLocation();
  const { repoId } = useParams();
  const toggleCopilotPanel = useUiStore((s) => s.toggleCopilotPanel);
  const setCopilotPanelOpen = useUiStore((s) => s.setCopilotPanelOpen);
  const toggleSidebarCollapsed = useUiStore((s) => s.toggleSidebarCollapsed);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const tag = target?.tagName?.toLowerCase();
      const editing =
        tag === 'input' ||
        tag === 'textarea' ||
        tag === 'select' ||
        target?.isContentEditable;

      if (event.key === 'Escape') {
        setCopilotPanelOpen(false);
        return;
      }

      const meta = event.metaKey || event.ctrlKey;
      if (!meta) return;

      const key = event.key.toLowerCase();

      if (key === 'j') {
        event.preventDefault();
        toggleCopilotPanel();
        return;
      }

      if (key === 'b') {
        event.preventDefault();
        toggleSidebarCollapsed();
        return;
      }

      if (key === 'k' && !editing) {
        event.preventDefault();
        if (repoId) {
          const searchPath = `/dashboard/${repoId}/search`;
          if (location.pathname !== searchPath) {
            navigate(searchPath);
          } else {
            const input = document.querySelector<HTMLInputElement>(
              'input[data-search-input], input[type="search"], input[placeholder*="Search" i]'
            );
            input?.focus();
          }
        }
      }
    };

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [
    location.pathname,
    navigate,
    repoId,
    setCopilotPanelOpen,
    toggleCopilotPanel,
    toggleSidebarCollapsed,
  ]);
}
