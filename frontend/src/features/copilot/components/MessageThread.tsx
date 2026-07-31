import { useEffect, useRef } from 'react';
import type { CopilotMessageView } from '../api/copilot.types';
import { MessageBubble } from './MessageBubble';

interface MessageThreadProps {
  messages: CopilotMessageView[];
  onRetry?: () => void;
  onFollowUp?: (question: string) => void;
}

export function MessageThread({ messages, onRetry, onFollowUp }: MessageThreadProps) {
  const endRef = useRef<HTMLDivElement>(null);

  const lastContent = messages[messages.length - 1]?.content;

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length, lastContent]);

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 p-6 text-center">
        <h2 className="text-sm font-medium text-text-primary">Ask anything about your codebase</h2>
        <p className="max-w-md text-sm text-text-secondary">
          Copilot uses repository intelligence modules to answer architecture, risk, and
          implementation questions. Responses are JSON today — streaming can plug in later.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-4 overflow-y-auto p-4">
      {messages.map((message, index) => (
        <MessageBubble
          key={message.id}
          message={message}
          onRetry={
            message.status === 'error' && index === messages.length - 1 ? onRetry : undefined
          }
          onFollowUp={onFollowUp}
        />
      ))}
      <div ref={endRef} />
    </div>
  );
}
