import type { ReactNode } from 'react';

interface AuthGuardProps {
  children: ReactNode;
}

/**
 * Route protection wrapper.
 * Currently a passthrough. Will redirect to /login when auth is implemented.
 */
export function AuthGuard({ children }: AuthGuardProps) {
  return <>{children}</>;
}
