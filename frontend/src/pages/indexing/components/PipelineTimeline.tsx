import { cn } from '@/lib/cn';
import type { IndexingStep } from '@/features/indexing/api/indexing.types';

interface PipelineTimelineProps {
  steps: IndexingStep[];
}

const stepDescriptions: Record<string, string> = {
  scanning: 'Scanning repository files',
  parsing: 'Parsing source code',
  indexing: 'Building index',
  embedding: 'Creating embeddings',
  analyzing: 'Analyzing code',
  ready: 'Analysis complete',
};

export function PipelineTimeline({ steps }: PipelineTimelineProps) {
  return (
    <div className="space-y-4">
      {steps.map((step, index) => (
        <div key={step.id} className="flex gap-4">
          <div className="flex flex-col items-center">
            <StepIcon status={step.status} />
            {index < steps.length - 1 && (
              <div className="my-2 h-full w-px bg-border-subtle" />
            )}
          </div>
          <div className="flex-1 space-y-1">
            <div
              className={cn(
                'text-sm font-medium',
                step.status === 'complete' && 'text-text-primary',
                step.status === 'active' && 'text-accent-default',
                step.status === 'pending' && 'text-text-tertiary',
                step.status === 'error' && 'text-danger'
              )}
            >
              {step.label}
            </div>
            <div className="text-xs text-text-secondary">
              {stepDescriptions[step.id] || ''}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function StepIcon({ status }: { status: IndexingStep['status'] }) {
  if (status === 'complete') {
    return (
      <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-success/20 text-success">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M10 3L4.5 8.5L2 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>
    );
  }
  if (status === 'active') {
    return (
      <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent-subtle text-accent-default">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" className="animate-spin">
          <path d="M10 6C10 8.20914 8.20914 10 6 10C3.79086 10 2 8.20914 2 6C2 3.79086 3.79086 2 6 2C7.30622 2 8.41735 2.66615 9.05001 3.65" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>
    );
  }
  if (status === 'error') {
    return (
      <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-danger/20 text-danger">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 3L3 9M3 3L9 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>
    );
  }
  return (
    <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-bg-subtle border border-border-subtle text-text-tertiary">
      <div className="h-2 w-2 rounded-full bg-text-tertiary" />
    </div>
  );
}
