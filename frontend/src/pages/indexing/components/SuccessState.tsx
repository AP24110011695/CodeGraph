import { Link } from 'react-router-dom';
import { Button } from '@/design-system/primitives/Button';

interface SuccessStateProps {
  repoId: string;
}

export function SuccessState({ repoId }: SuccessStateProps) {
  return (
    <div className="rounded-xl border border-border-subtle bg-bg-elevated p-8 text-center">
      <div className="mb-4 flex justify-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-success/20 text-success">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M26 8L12 22L6 16" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      </div>
      <h2 className="mb-2 text-xl font-medium text-text-primary">Repository indexed successfully</h2>
      <p className="mb-6 text-sm text-text-secondary">
        Your repository is ready for analysis and exploration.
      </p>
      <div className="flex flex-wrap justify-center gap-3">
        <Link to={`/dashboard/${repoId}`}>
          <Button variant="primary" size="md">
            Open Repository
          </Button>
        </Link>
        <Link to={`/dashboard/${repoId}/copilot`}>
          <Button variant="secondary" size="md">
            Open Copilot
          </Button>
        </Link>
        <Link to={`/dashboard/${repoId}/architecture`}>
          <Button variant="secondary" size="md">
            Analyze Architecture
          </Button>
        </Link>
      </div>
    </div>
  );
}
