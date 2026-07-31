import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { deleteRepository, fetchRepositories } from './repositories.api';

export const repositoryKeys = {
  all: ['repositories'] as const,
  list: () => ['repositories', 'list'] as const,
  detail: (id: string) => ['repositories', 'detail', id] as const,
};

export function useRepositoriesQuery(enabled = true) {
  return useQuery({
    queryKey: repositoryKeys.list(),
    queryFn: fetchRepositories,
    enabled,
    staleTime: 30_000,
  });
}

export function useDeleteRepositoryMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ['repositories', 'delete'],
    mutationFn: (id: string) => deleteRepository(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: repositoryKeys.all });
      await queryClient.invalidateQueries();
    },
  });
}
