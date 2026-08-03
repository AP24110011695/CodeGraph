import { RouterProvider } from 'react-router-dom';
import { Providers } from './providers';
import { router } from './router';
import { ErrorBoundary } from '@/design-system/components/ErrorBoundary';
import { ToastContainer } from '@/design-system/primitives/Toast';
import { useEffect } from 'react';
import { clearLegacyRoutingState } from '@/core/navigation/flow-session';

export default function App() {
  useEffect(() => {
    clearLegacyRoutingState();
  }, []);

  return (
    <ErrorBoundary fallbackTitle="CodeGraph failed to load">
      <Providers>
        <RouterProvider router={router} />
        <ToastContainer />
      </Providers>
    </ErrorBoundary>
  );
}
