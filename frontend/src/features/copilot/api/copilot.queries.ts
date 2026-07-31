import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { clearCopilotHistory, fetchCopilotHistory, postCopilotChat } from './copilot.api';
import type { CopilotChatRequest } from './copilot.types';

export const copilotKeys = {
  all: ['copilot'] as const,
  history: (repoId: string, conversationId?: string | null) =>
    ['copilot', 'history', repoId, conversationId ?? 'all'] as const,
};

export function useCopilotChatMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ['copilot', 'chat'],
    mutationFn: (payload: CopilotChatRequest) => postCopilotChat(payload),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: copilotKeys.history(variables.repository_id, variables.conversation_id),
      });
    },
  });
}

export function useCopilotHistoryQuery(repoId: string, conversationId?: string | null) {
  return useQuery({
    queryKey: copilotKeys.history(repoId, conversationId),
    queryFn: () =>
      fetchCopilotHistory({
        repositoryId: repoId,
        conversationId: conversationId ?? undefined,
      }),
    enabled: Boolean(repoId),
    staleTime: 30_000,
  });
}

export function useClearCopilotHistoryMutation(repoId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (conversationId?: string) =>
      clearCopilotHistory({ repositoryId: repoId, conversationId }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['copilot', 'history', repoId] });
    },
  });
}
