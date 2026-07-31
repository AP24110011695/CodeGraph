import { apiClient } from '@/core/api/client';
import type {
  CopilotChatRequest,
  CopilotChatResponse,
  CopilotHistoryResponse,
} from './copilot.types';

export async function postCopilotChat(
  payload: CopilotChatRequest
): Promise<CopilotChatResponse> {
  const { data } = await apiClient.post<CopilotChatResponse>('/copilot/chat', payload, {
    timeout: 120_000,
  });
  return data;
}

export async function fetchCopilotHistory(params: {
  repositoryId?: string;
  conversationId?: string;
  limit?: number;
}): Promise<CopilotHistoryResponse> {
  const { data } = await apiClient.get<CopilotHistoryResponse>('/copilot/history', {
    params: {
      repository_id: params.repositoryId,
      conversation_id: params.conversationId,
      limit: params.limit ?? 50,
    },
  });
  return data;
}

export async function clearCopilotHistory(params: {
  repositoryId?: string;
  conversationId?: string;
}): Promise<void> {
  await apiClient.delete('/copilot/history', {
    params: {
      repository_id: params.repositoryId,
      conversation_id: params.conversationId,
    },
  });
}
