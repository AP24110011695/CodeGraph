import { Check, Circle, Loader2, X } from 'lucide-react';
import { cn } from '@/lib/cn';
import type { IndexingStep } from '../api/indexing.types';

interface IndexingProgressStepperProps {
  steps: IndexingStep[];
}

export function IndexingProgressStepper({ steps }: IndexingProgressStepperProps) {
  return (
    <ol className="space-y-3">
      {steps.map((step) => (
        <li key={step.id} className="flex items-center gap-3">
          <StepIcon status={step.status} />
          <span
            className={cn(
              'text-sm',
              step.status === 'complete' && 'text-text-primary',
              step.status === 'active' && 'font-medium text-text-primary',
              step.status === 'pending' && 'text-text-tertiary',
              step.status === 'error' && 'text-danger'
            )}
          >
            {step.label}
          </span>
        </li>
      ))}
    </ol>
  );
}

function StepIcon({ status }: { status: IndexingStep['status'] }) {
  if (status === 'complete') {
    return (
      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-success/15 text-success">
        <Check className="h-3.5 w-3.5" aria-hidden />
      </span>
    );
  }
  if (status === 'active') {
    return (
      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-accent-subtle text-accent-default">
        <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden />
      </span>
    );
  }
  if (status === 'error') {
    return (
      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-danger/15 text-danger">
        <X className="h-3.5 w-3.5" aria-hidden />
      </span>
    );
  }
  return (
    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-bg-subtle text-text-tertiary">
      <Circle className="h-3 w-3" aria-hidden />
    </span>
  );
}
