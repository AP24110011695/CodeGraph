import { RouterProvider } from 'react-router-dom';
import { Providers } from './providers';
import { router } from './router';
import { ErrorBoundary } from '@/design-system/components/ErrorBoundary';
import { ToastContainer } from '@/design-system/primitives/Toast';

export default function App() {
  return (
    <ErrorBoundary fallbackTitle="CodeGraph failed to load">
      <Providers>
        <RouterProvider router={router} />
        <ToastContainer />
      </Providers>
    </ErrorBoundary>
  );
}
