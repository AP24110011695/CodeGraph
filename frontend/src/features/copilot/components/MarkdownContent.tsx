import ReactMarkdown from 'react-markdown';
import { cn } from '@/lib/cn';

interface MarkdownContentProps {
  content: string;
  className?: string;
}

export function MarkdownContent({ content, className }: MarkdownContentProps) {
  return (
    <div className={cn('space-y-2 text-sm leading-relaxed text-text-secondary', className)}>
      <ReactMarkdown
        components={{
          h1: ({ children }) => (
            <h1 className="text-base font-medium text-text-primary">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-sm font-medium text-text-primary">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-sm font-medium text-text-primary">{children}</h3>
          ),
          p: ({ children }) => <p className="text-sm text-text-secondary">{children}</p>,
          ul: ({ children }) => (
            <ul className="list-disc space-y-1 pl-5 text-sm text-text-secondary">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal space-y-1 pl-5 text-sm text-text-secondary">{children}</ol>
          ),
          a: ({ href, children }) => (
            <a
              href={href}
              className="text-accent-default hover:underline"
              target="_blank"
              rel="noreferrer"
            >
              {children}
            </a>
          ),
          code: ({ className: codeClassName, children }) => {
            const isBlock = Boolean(codeClassName);
            if (!isBlock) {
              return (
                <code className="rounded bg-bg-subtle px-1 py-0.5 font-mono text-[12px] text-syntax-keyword">
                  {children}
                </code>
              );
            }
            return (
              <pre className="overflow-x-auto rounded-md border border-border-base bg-bg-base p-3 font-mono text-[12px] text-text-primary">
                <code>{children}</code>
              </pre>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
