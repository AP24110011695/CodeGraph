import { Plus, Trash2 } from 'lucide-react';
import { Button } from '@/design-system/primitives/Button';
import { cn } from '@/lib/cn';
import { useCopilotSessionStore } from '../store/copilot.session.store';

interface ConversationSidebarProps {
  repositoryId: string;
  onNew: () => void;
  onClear: () => void;
}

export function ConversationSidebar({ repositoryId, onNew, onClear }: ConversationSidebarProps) {
  const conversations = useCopilotSessionStore((s) => s.conversations);
  const activeConversationId = useCopilotSessionStore((s) => s.activeConversationId);
  const setActiveConversation = useCopilotSessionStore((s) => s.setActiveConversation);

  const items = Object.values(conversations)
    .filter((conversation) => conversation.repositoryId === repositoryId)
    .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));

  return (
    <aside className="flex h-full w-56 shrink-0 flex-col border-r border-border-base bg-bg-elevated">
      <div className="flex items-center justify-between gap-2 border-b border-border-base p-3">
        <h2 className="text-sm font-medium text-text-primary">Conversations</h2>
        <Button variant="ghost" size="sm" onClick={onNew} aria-label="New conversation">
          <Plus className="h-4 w-4" />
        </Button>
      </div>
      <div className="flex-1 space-y-1 overflow-y-auto p-2">
        {items.length === 0 && (
          <p className="px-2 py-3 text-xs text-text-tertiary">No conversations yet</p>
        )}
        {items.map((conversation) => (
          <button
            key={conversation.id}
            type="button"
            onClick={() => setActiveConversation(conversation.id)}
            className={cn(
              'w-full rounded-md px-2 py-2 text-left text-xs text-text-secondary hover:bg-bg-subtle hover:text-text-primary',
              activeConversationId === conversation.id && 'bg-accent-subtle text-text-primary'
            )}
          >
            <p className="truncate font-medium">{conversation.title || 'Untitled'}</p>
            <p className="mt-0.5 text-[10px] text-text-tertiary">
              {conversation.messages.length} messages
            </p>
          </button>
        ))}
      </div>
      <div className="border-t border-border-base p-2">
        <Button variant="ghost" size="sm" className="w-full justify-start" onClick={onClear}>
          <Trash2 className="h-3.5 w-3.5" />
          Clear local history
        </Button>
      </div>
    </aside>
  );
}
