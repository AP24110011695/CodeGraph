import ReactMarkdown from 'react-markdown';
import { cn } from '@/lib/cn';

interface MarkdownContentProps {
  content: string;
  className?: string;
}

export function MarkdownContent({ content, className }: MarkdownContentProps) {
  return (
    <div className={cn('max-w-4xl space-y-4 text-base leading-relaxed text-text-secondary', className)}>
      <ReactMarkdown
        components={{
          h1: ({ children }) => (
            <h1 className="text-2xl font-bold text-text-primary tracking-tight mb-4 mt-8 pb-2 border-b border-border-base">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-xl font-semibold text-text-primary tracking-tight mb-3 mt-6">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-lg font-medium text-text-primary mb-2 mt-5">{children}</h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-base font-medium text-text-primary mb-2 mt-4">{children}</h4>
          ),
          p: ({ children }) => <p className="text-sm text-text-secondary leading-relaxed mb-4">{children}</p>,
          ul: ({ children }) => (
            <ul className="list-disc space-y-2 pl-6 text-sm text-text-secondary mb-4">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal space-y-2 pl-6 text-sm text-text-secondary mb-4">{children}</ol>
          ),
          li: ({ children }) => <li className="text-sm text-text-secondary leading-relaxed">{children}</li>,
          a: ({ href, children }) => (
            <a
              href={href}
              className="text-accent-default hover:underline font-medium"
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
                <code className="rounded-md border border-border-base bg-[#121110] px-1.5 py-0.5 font-mono text-[12px] text-syntax-keyword">
                  {children}
                </code>
              );
            }
            return (
              <pre className="overflow-x-auto rounded-2xl border border-border-base bg-[#121110] p-4 font-mono text-[13px] text-text-primary mb-6 shadow-inner">
                <code>{children}</code>
              </pre>
            );
          },
          table: ({ children }) => (
            <div className="overflow-x-auto my-6 rounded-2xl border border-border-base bg-[#181614] shadow-xl">
              <table className="min-w-full divide-y divide-border-base">{children}</table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-[#121110]">{children}</thead>
          ),
          tbody: ({ children }) => (
            <tbody className="divide-y divide-border-base bg-[#181614]">{children}</tbody>
          ),
          tr: ({ children }) => (
            <tr className="hover:bg-[#2A2420] transition-colors">{children}</tr>
          ),
          th: ({ children }) => (
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-text-primary border-b border-border-base">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-3 text-sm text-text-secondary">{children}</td>
          ),
          hr: () => <hr className="my-8 border-border-base" />,
          strong: ({ children }) => (
            <strong className="font-semibold text-text-primary">{children}</strong>
          ),
          blockquote: ({ children }) => (
            <blockquote className="rounded-xl border-l-4 border-accent-default bg-accent-subtle/30 px-4 py-3 italic text-text-secondary mb-4 shadow-sm">
              {children}
            </blockquote>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

