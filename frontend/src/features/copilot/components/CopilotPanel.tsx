import { useCallback, useEffect } from 'react';
import { PanelRightOpen, PanelRightClose } from 'lucide-react';
import { Button } from '@/design-system/primitives/Button';
import { isAPIError } from '@/core/api/errors';
import {
  adaptChatResponseToContext,
  adaptChatResponseToMessage,
} from '../api/copilot.adapters';
import { useClearCopilotHistoryMutation, useCopilotChatMutation } from '../api/copilot.queries';
import { useCopilotSessionStore } from '../store/copilot.session.store';
import { ContextPanel } from './ContextPanel';
import { ConversationSidebar } from './ConversationSidebar';
import { MessageInput } from './MessageInput';
import { MessageThread } from './MessageThread';

interface CopilotPanelProps {
  repoId: string;
}

export function CopilotPanel({ repoId }: CopilotPanelProps) {
  const conversations = useCopilotSessionStore((s) => s.conversations);
  const activeConversationId = useCopilotSessionStore((s) => s.activeConversationId);
  const contextPanelOpen = useCopilotSessionStore((s) => s.contextPanelOpen);
  const latestContext = useCopilotSessionStore((s) => s.latestContext);
  const isAwaitingResponse = useCopilotSessionStore((s) => s.isAwaitingResponse);
  const createConversation = useCopilotSessionStore((s) => s.createConversation);
  const setActiveConversation = useCopilotSessionStore((s) => s.setActiveConversation);
  const addMessage = useCopilotSessionStore((s) => s.addMessage);
  const updateMessage = useCopilotSessionStore((s) => s.updateMessage);
  const setLatestContext = useCopilotSessionStore((s) => s.setLatestContext);
  const setContextPanelOpen = useCopilotSessionStore((s) => s.setContextPanelOpen);
  const setAwaitingResponse = useCopilotSessionStore((s) => s.setAwaitingResponse);
  const clearRepositoryConversations = useCopilotSessionStore(
    (s) => s.clearRepositoryConversations
  );

  const chatMutation = useCopilotChatMutation();
  const clearHistoryMutation = useClearCopilotHistoryMutation(repoId);

  useEffect(() => {
    if (!activeConversationId || !conversations[activeConversationId]) {
      createConversation(repoId);
    }
  }, [activeConversationId, conversations, createConversation, repoId]);

  const activeConversation = activeConversationId
    ? conversations[activeConversationId]
    : undefined;

  const ensureConversation = useCallback(() => {
    if (activeConversationId && conversations[activeConversationId]) {
      return activeConversationId;
    }
    return createConversation(repoId);
  }, [activeConversationId, conversations, createConversation, repoId]);

  const sendMessage = useCallback(
    async (query: string, options?: { retryAssistantId?: string }) => {
      const conversationId = ensureConversation();
      const userMessageId = crypto.randomUUID();
      const assistantMessageId = options?.retryAssistantId ?? crypto.randomUUID();

      if (!options?.retryAssistantId) {
        addMessage(conversationId, {
          id: userMessageId,
          role: 'user',
          content: query,
          createdAt: new Date().toISOString(),
          status: 'complete',
        });
        addMessage(conversationId, {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
          createdAt: new Date().toISOString(),
          status: 'pending',
        });
      } else {
        updateMessage(conversationId, assistantMessageId, {
          status: 'pending',
          content: '',
          error: undefined,
        });
      }

      setAwaitingResponse(true);
      setLatestContext(null);

      try {
        // JSON response today. Streaming hooks remain available on the session store for SSE later.
        const response = await chatMutation.mutateAsync({
          repository_id: repoId,
          query,
          conversation_id: conversationId,
        });

        const backendConversationId = response.conversation_id || conversationId;
        if (backendConversationId !== conversationId) {
          setActiveConversation(backendConversationId);
        }

        const adapted = adaptChatResponseToMessage(response, assistantMessageId);
        updateMessage(conversationId, assistantMessageId, adapted);
        setLatestContext(adaptChatResponseToContext(response));
      } catch (error) {
        updateMessage(conversationId, assistantMessageId, {
          status: 'error',
          content: 'I encountered an error analyzing your codebase.',
          error: isAPIError(error) ? error.message : 'Request failed',
        });
      } finally {
        setAwaitingResponse(false);
      }
    },
    [
      addMessage,
      chatMutation,
      ensureConversation,
      repoId,
      setActiveConversation,
      setAwaitingResponse,
      setLatestContext,
      updateMessage,
    ]
  );

  const lastUserMessage = [...(activeConversation?.messages ?? [])]
    .reverse()
    .find((message) => message.role === 'user');

  const lastAssistant = [...(activeConversation?.messages ?? [])]
    .reverse()
    .find((message) => message.role === 'assistant');

  return (
    <div className="flex h-[calc(100vh-3rem)] min-h-[480px]">
      <ConversationSidebar
        repositoryId={repoId}
        onNew={() => createConversation(repoId)}
        onClear={() => {
          clearRepositoryConversations(repoId);
          void clearHistoryMutation.mutateAsync(undefined);
          createConversation(repoId);
        }}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <div className="flex items-center justify-between border-b border-border-base px-4 py-2">
          <div>
            <h1 className="text-sm font-medium text-text-primary">Copilot</h1>
            <p className="text-xs text-text-tertiary">
              POST /copilot/chat · JSON responses (SSE-ready store)
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setContextPanelOpen(!contextPanelOpen)}
            aria-label={contextPanelOpen ? 'Hide context panel' : 'Show context panel'}
          >
            {contextPanelOpen ? (
              <PanelRightClose className="h-4 w-4" />
            ) : (
              <PanelRightOpen className="h-4 w-4" />
            )}
            Context
          </Button>
        </div>

        <MessageThread
          messages={activeConversation?.messages ?? []}
          onFollowUp={(question) => void sendMessage(question)}
          onRetry={() => {
            if (!lastUserMessage || !lastAssistant) return;
            void sendMessage(lastUserMessage.content, {
              retryAssistantId: lastAssistant.id,
            });
          }}
        />

        <MessageInput
          disabled={isAwaitingResponse || chatMutation.isPending}
          onSend={(value) => void sendMessage(value)}
        />
      </div>

      {contextPanelOpen && (
        <aside className="flex w-80 shrink-0 flex-col border-l border-border-base bg-bg-elevated">
          <div className="border-b border-border-base px-4 py-3">
            <h2 className="text-sm font-medium text-text-primary">Context</h2>
            <p className="text-xs text-text-tertiary">Sources used for the latest answer</p>
          </div>
          <ContextPanel context={latestContext} loading={isAwaitingResponse} />
        </aside>
      )}
    </div>
  );
}
