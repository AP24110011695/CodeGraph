import { Badge } from '@/design-system/primitives/Badge';
import { Button } from '@/design-system/primitives/Button';
import { cn } from '@/lib/cn';
import type { CopilotMessageView } from '../api/copilot.types';
import { MarkdownContent } from './MarkdownContent';

interface MessageBubbleProps {
  message: CopilotMessageView;
  onRetry?: () => void;
  onFollowUp?: (question: string) => void;
}

export function MessageBubble({ message, onRetry, onFollowUp }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={cn('flex w-full', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[85%] rounded-md px-3 py-2',
          isUser
            ? 'bg-accent-subtle text-text-primary'
            : 'border border-border-base bg-bg-elevated text-text-secondary'
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        ) : (
          <>
            {message.status === 'pending' ? (
              <p className="text-sm text-text-tertiary" aria-live="polite">
                Thinking…
              </p>
            ) : (
              <MarkdownContent content={message.content} />
            )}

            {message.status === 'error' && (
              <div className="mt-2 space-y-2">
                <p className="text-xs text-danger">{message.error ?? 'Request failed'}</p>
                {onRetry && (
                  <Button variant="danger" size="sm" onClick={onRetry}>
                    Retry
                  </Button>
                )}
              </div>
            )}

            {message.status === 'complete' && (
              <div className="mt-3 flex flex-wrap items-center gap-2">
                {typeof message.confidence === 'number' && (
                  <Badge variant="info">
                    Confidence {Math.round(message.confidence * 100)}%
                  </Badge>
                )}
                {(message.citations?.length ?? 0) > 0 && (
                  <Badge variant="default">{message.citations?.length} citations</Badge>
                )}
              </div>
            )}

            {(message.followUpQuestions?.length ?? 0) > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {message.followUpQuestions?.map((question) => (
                  <button
                    key={question}
                    type="button"
                    className="rounded-md border border-border-base px-2 py-1 text-xs text-text-secondary hover:border-border-strong hover:text-text-primary"
                    onClick={() => onFollowUp?.(question)}
                  >
                    {question}
                  </button>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
