import { Check, Circle, Loader2, X } from 'lucide-react';
import { cn } from '@/lib/cn';
import type { IndexingStep } from '../api/indexing.types';

interface IndexingProgressStepperProps {
  steps: IndexingStep[];
}

export function IndexingProgressStepper({ steps }: IndexingProgressStepperProps) {
  return (
    <ol className="space-y-3.5">
      {steps.map((step) => (
        <li key={step.id} className="flex items-center gap-3.5">
          <StepIcon status={step.status} />
          <span
            className={cn(
              'text-xs tracking-tight transition-colors',
              step.status === 'complete' && 'font-medium text-text-primary',
              step.status === 'active' && 'font-semibold text-accent-default',
              step.status === 'pending' && 'text-text-tertiary',
              step.status === 'error' && 'font-medium text-danger'
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
      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[#34C759]/20 text-[#34C759] shadow-[0_0_12px_rgba(52,199,89,0.35)]">
        <Check className="h-3.5 w-3.5" aria-hidden />
      </span>
    );
  }
  if (status === 'active') {
    return (
      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-accent-subtle text-accent-default animate-pulse shadow-[0_0_12px_rgba(232,160,69,0.35)]">
        <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden />
      </span>
    );
  }
  if (status === 'error') {
    return (
      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-danger/20 text-danger shadow-[0_0_12px_rgba(255,92,92,0.35)]">
        <X className="h-3.5 w-3.5" aria-hidden />
      </span>
    );
  }
  return (
    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[#121110] border border-border-base text-text-tertiary">
      <Circle className="h-3 w-3" aria-hidden />
    </span>
  );
}

