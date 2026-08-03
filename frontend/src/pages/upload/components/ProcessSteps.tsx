interface StepProps {
  num: number;
  title: string;
}

function Step({ num, title }: StepProps) {
  return (
    <div className="flex items-start gap-3">
      <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent-subtle text-xs font-medium text-accent-default">
        {num}
      </div>
      <span className="text-sm text-text-secondary">{title}</span>
    </div>
  );
}

export function ProcessSteps() {
  return (
    <div className="rounded-xl border border-border-subtle bg-bg-elevated p-6">
      <h3 className="mb-4 text-base font-medium text-text-primary">What happens next?</h3>
      <div className="space-y-3">
        <Step num={1} title="Scan files" />
        <Step num={2} title="Detect frameworks" />
        <Step num={3} title="Build architecture graph" />
        <Step num={4} title="Analyze code quality" />
        <Step num={5} title="AI generates insights" />
      </div>
    </div>
  );
}
