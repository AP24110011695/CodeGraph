import { useQuery } from '@tanstack/react-query';
import { analyzeSecurity } from './security.api';

export const securityKeys = {
  all: ['security'] as const,
  security: (repoId: string) => ['security', repoId] as const,
};

export function useSecurityQuery(repoId: string) {
  return useQuery({
    queryKey: securityKeys.security(repoId),
    queryFn: () => analyzeSecurity(repoId),
    enabled: Boolean(repoId),
    staleTime: 10 * 60 * 1000,
  });
}
