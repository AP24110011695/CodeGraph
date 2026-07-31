import { create } from 'zustand';

export interface CopilotMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: CopilotMessage[];
  createdAt: string;
  updatedAt: string;
}

interface CopilotState {
  conversations: Record<string, Conversation>;
  activeConversationId: string | null;
  streamingMessageId: string | null;
  streamingContent: string;
  addMessage: (conversationId: string, message: CopilotMessage) => void;
  appendStreamToken: (token: string) => void;
  finalizeStreamingMessage: () => void;
  createConversation: (title?: string) => string;
  setActiveConversation: (id: string | null) => void;
  clearConversations: () => void;
}

function createId(prefix: string): string {
  return `${prefix}_${crypto.randomUUID()}`;
}

export const useCopilotStore = create<CopilotState>((set, get) => ({
  conversations: {},
  activeConversationId: null,
  streamingMessageId: null,
  streamingContent: '',
  addMessage: (conversationId, message) =>
    set((state) => {
      const conversation = state.conversations[conversationId];
      if (!conversation) return state;
      return {
        conversations: {
          ...state.conversations,
          [conversationId]: {
            ...conversation,
            messages: [...conversation.messages, message],
            updatedAt: new Date().toISOString(),
          },
        },
      };
    }),
  appendStreamToken: (token) =>
    set((state) => ({
      streamingContent: `${state.streamingContent}${token}`,
    })),
  finalizeStreamingMessage: () => {
    const { activeConversationId, streamingMessageId, streamingContent } = get();
    if (!activeConversationId || !streamingMessageId) {
      set({ streamingMessageId: null, streamingContent: '' });
      return;
    }

    get().addMessage(activeConversationId, {
      id: streamingMessageId,
      role: 'assistant',
      content: streamingContent,
      createdAt: new Date().toISOString(),
    });
    set({ streamingMessageId: null, streamingContent: '' });
  },
  createConversation: (title = 'New conversation') => {
    const id = createId('conv');
    const now = new Date().toISOString();
    set((state) => ({
      conversations: {
        ...state.conversations,
        [id]: {
          id,
          title,
          messages: [],
          createdAt: now,
          updatedAt: now,
        },
      },
      activeConversationId: id,
    }));
    return id;
  },
  setActiveConversation: (id) => set({ activeConversationId: id }),
  clearConversations: () =>
    set({
      conversations: {},
      activeConversationId: null,
      streamingMessageId: null,
      streamingContent: '',
    }),
}));
