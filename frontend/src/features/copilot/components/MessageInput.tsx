import { useState, type FormEvent, type KeyboardEvent } from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/design-system/primitives/Button';

interface MessageInputProps {
  disabled?: boolean;
  onSend: (value: string) => void;
}

const SUGGESTIONS = [
  'Summarize the architecture of this repository',
  'What are the top risks?',
  'Which modules are most coupled?',
  'Explain the main entry points',
];

export function MessageInput({ disabled, onSend }: MessageInputProps) {
  const [value, setValue] = useState('');

  const submit = (event?: FormEvent) => {
    event?.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
  };

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };

  return (
    <div className="border-t border-border-base p-3">
      <div className="mb-2 flex flex-wrap gap-2">
        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            disabled={disabled}
            className="rounded-md border border-border-base px-2 py-1 text-[11px] text-text-tertiary hover:border-border-strong hover:text-text-secondary disabled:opacity-50"
            onClick={() => onSend(suggestion)}
          >
            {suggestion}
          </button>
        ))}
      </div>
      <form onSubmit={submit} className="flex items-end gap-2">
        <textarea
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={onKeyDown}
          disabled={disabled}
          rows={2}
          placeholder="Ask about architecture, risks, modules…"
          className="min-h-[56px] flex-1 resize-none rounded-md border border-border-base bg-bg-elevated px-3 py-2 text-sm text-text-primary placeholder:text-text-tertiary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-default"
        />
        <Button type="submit" variant="primary" size="md" disabled={disabled || !value.trim()}>
          <Send className="h-4 w-4" />
          Send
        </Button>
      </form>
    </div>
  );
}
