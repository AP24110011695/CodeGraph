import { Outlet } from 'react-router-dom';
import { Bot } from 'lucide-react';
import { cn } from '@/lib/cn';
import { useUiStore } from '@/core/store/ui.store';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import { Button } from '@/design-system/primitives/Button';
import { TopBar } from './TopBar';
import { Sidebar } from './Sidebar';

/**
 * Persistent dashboard shell: TopBar + Sidebar + Outlet.
 * Copilot panel chrome is present but empty until Phase 5.
 */
export default function DashboardLayout() {
  useKeyboardShortcuts();
  const copilotPanelOpen = useUiStore((s) => s.copilotPanelOpen);
  const toggleCopilotPanel = useUiStore((s) => s.toggleCopilotPanel);

  return (
    <div className="flex h-screen flex-col bg-bg-base text-text-primary">
      <TopBar />
      <div className="relative flex min-h-0 flex-1">
        <Sidebar />
        <main className="min-w-0 flex-1 overflow-auto">
          <Outlet />
        </main>
        <aside
          className={cn(
            'shrink-0 overflow-hidden border-l border-border-base bg-bg-elevated transition-[width] duration-normal ease-out-expo',
            copilotPanelOpen ? 'w-copilot-panel' : 'w-0 border-l-0'
          )}
          aria-hidden={!copilotPanelOpen}
        >
          <div className="flex h-full w-copilot-panel flex-col p-4">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-medium text-text-primary">Copilot</h2>
              <Button variant="ghost" size="sm" onClick={toggleCopilotPanel} aria-label="Close copilot">
                Close
              </Button>
            </div>
            <p className="text-sm text-text-secondary">
              Copilot chat will be implemented in a later phase.
            </p>
          </div>
        </aside>
        {!copilotPanelOpen && (
          <Button
            variant="secondary"
            size="sm"
            className="absolute bottom-4 right-4 shadow-none"
            onClick={toggleCopilotPanel}
            aria-label="Open copilot panel"
          >
            <Bot className="h-4 w-4" />
            Copilot
          </Button>
        )}
      </div>
    </div>
  );
}
