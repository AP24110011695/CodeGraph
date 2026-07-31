import { Link, Outlet, useParams } from 'react-router-dom';
import { Bot } from 'lucide-react';
import { cn } from '@/lib/cn';
import { useUiStore } from '@/core/store/ui.store';
import { PageTransition } from '@/core/components/PageTransition';
import { ErrorBoundary } from '@/design-system/components/ErrorBoundary';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import { Button } from '@/design-system/primitives/Button';
import { TopBar } from './TopBar';
import { Sidebar } from './Sidebar';

/**
 * Persistent dashboard shell: TopBar + Sidebar + Outlet.
 * Floating copilot entry opens the full Phase 5 page.
 */
export default function DashboardLayout() {
  useKeyboardShortcuts();
  const { repoId } = useParams();
  const copilotPanelOpen = useUiStore((s) => s.copilotPanelOpen);
  const toggleCopilotPanel = useUiStore((s) => s.toggleCopilotPanel);

  return (
    <div className="flex h-screen flex-col bg-bg-base text-text-primary">
      <a
        href="#dashboard-main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-accent-default focus:px-3 focus:py-2 focus:text-sm focus:text-white"
      >
        Skip to content
      </a>
      <TopBar />
      <div className="relative flex min-h-0 flex-1">
        <Sidebar />
        <main id="dashboard-main" className="min-w-0 flex-1 overflow-auto" tabIndex={-1}>
          <ErrorBoundary fallbackTitle="This page failed to render">
            <PageTransition>
              <Outlet />
            </PageTransition>
          </ErrorBoundary>
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
            <p className="mb-4 text-sm text-text-secondary">
              Open the full copilot workspace for chat, context, and conversation history.
            </p>
            {repoId && (
              <Link to={`/dashboard/${repoId}/copilot`} onClick={() => toggleCopilotPanel()}>
                <Button variant="primary" size="sm">
                  Open Copilot
                </Button>
              </Link>
            )}
          </div>
        </aside>
        {!copilotPanelOpen && repoId && (
          <Link
            to={`/dashboard/${repoId}/copilot`}
            className="absolute bottom-4 right-4"
            aria-label="Open copilot page"
          >
            <Button variant="secondary" size="sm" className="shadow-none">
              <Bot className="h-4 w-4" />
              Copilot
            </Button>
          </Link>
        )}
      </div>
    </div>
  );
}
