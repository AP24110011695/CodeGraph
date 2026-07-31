import { create } from 'zustand';
import type { CopilotContextSnapshot, CopilotMessageView } from '../api/copilot.types';

interface SessionConversation {
  id: string;
  title: string;
  repositoryId: string;
  messages: CopilotMessageView[];
  createdAt: string;
  updatedAt: string;
}

interface CopilotSessionState {
  conversations: Record<string, SessionConversation>;
  activeConversationId: string | null;
  contextPanelOpen: boolean;
  latestContext: CopilotContextSnapshot | null;
  isAwaitingResponse: boolean;
  /** Reserved for future SSE token buffering. */
  streamingMessageId: string | null;
  streamingContent: string;
  createConversation: (repositoryId: string, title?: string) => string;
  setActiveConversation: (id: string | null) => void;
  addMessage: (conversationId: string, message: CopilotMessageView) => void;
  updateMessage: (
    conversationId: string,
    messageId: string,
    patch: Partial<CopilotMessageView>
  ) => void;
  setLatestContext: (context: CopilotContextSnapshot | null) => void;
  setContextPanelOpen: (open: boolean) => void;
  setAwaitingResponse: (value: boolean) => void;
  /** Future SSE hook: append token into streaming buffer. */
  appendStreamToken: (token: string) => void;
  beginStreamingMessage: (messageId: string) => void;
  finalizeStreamingMessage: (conversationId: string) => void;
  clearRepositoryConversations: (repositoryId: string) => void;
}

function createId(prefix: string): string {
  return `${prefix}_${crypto.randomUUID()}`;
}

export const useCopilotSessionStore = create<CopilotSessionState>((set, get) => ({
  conversations: {},
  activeConversationId: null,
  contextPanelOpen: true,
  latestContext: null,
  isAwaitingResponse: false,
  streamingMessageId: null,
  streamingContent: '',
  createConversation: (repositoryId, title = 'New conversation') => {
    const id = createId('conv');
    const now = new Date().toISOString();
    set((state) => ({
      conversations: {
        ...state.conversations,
        [id]: {
          id,
          title,
          repositoryId,
          messages: [],
          createdAt: now,
          updatedAt: now,
        },
      },
      activeConversationId: id,
      latestContext: null,
    }));
    return id;
  },
  setActiveConversation: (id) => set({ activeConversationId: id }),
  addMessage: (conversationId, message) =>
    set((state) => {
      const conversation = state.conversations[conversationId];
      if (!conversation) return state;
      return {
        conversations: {
          ...state.conversations,
          [conversationId]: {
            ...conversation,
            title:
              conversation.messages.length === 0 && message.role === 'user'
                ? message.content.slice(0, 48)
                : conversation.title,
            messages: [...conversation.messages, message],
            updatedAt: new Date().toISOString(),
          },
        },
      };
    }),
  updateMessage: (conversationId, messageId, patch) =>
    set((state) => {
      const conversation = state.conversations[conversationId];
      if (!conversation) return state;
      return {
        conversations: {
          ...state.conversations,
          [conversationId]: {
            ...conversation,
            messages: conversation.messages.map((message) =>
              message.id === messageId ? { ...message, ...patch } : message
            ),
            updatedAt: new Date().toISOString(),
          },
        },
      };
    }),
  setLatestContext: (latestContext) => set({ latestContext }),
  setContextPanelOpen: (contextPanelOpen) => set({ contextPanelOpen }),
  setAwaitingResponse: (isAwaitingResponse) => set({ isAwaitingResponse }),
  appendStreamToken: (token) =>
    set((state) => ({ streamingContent: `${state.streamingContent}${token}` })),
  beginStreamingMessage: (messageId) =>
    set({ streamingMessageId: messageId, streamingContent: '' }),
  finalizeStreamingMessage: (conversationId) => {
    const { streamingMessageId, streamingContent } = get();
    if (!streamingMessageId) {
      set({ streamingMessageId: null, streamingContent: '' });
      return;
    }
    get().addMessage(conversationId, {
      id: streamingMessageId,
      role: 'assistant',
      content: streamingContent,
      createdAt: new Date().toISOString(),
      status: 'complete',
    });
    set({ streamingMessageId: null, streamingContent: '' });
  },
  clearRepositoryConversations: (repositoryId) =>
    set((state) => {
      const next: Record<string, SessionConversation> = {};
      for (const [id, conversation] of Object.entries(state.conversations)) {
        if (conversation.repositoryId !== repositoryId) {
          next[id] = conversation;
        }
      }
      const activeStillExists =
        state.activeConversationId != null && next[state.activeConversationId];
      return {
        conversations: next,
        activeConversationId: activeStillExists ? state.activeConversationId : null,
        latestContext: null,
      };
    }),
}));
