import { Link } from 'react-router-dom';
import { Button } from '@/design-system/primitives/Button';
import { beginUploadFlow } from '@/core/navigation/flow-session';

export function Hero() {
  return (
    <div className="flex flex-col items-center gap-8 text-center">
      <div className="inline-flex items-center rounded-full border border-border-subtle bg-bg-elevated px-4 py-1.5">
        <span className="text-xs text-text-secondary">AI-powered codebase analysis</span>
      </div>

      <div className="space-y-4">
        <h1 className="max-w-[700px] text-5xl font-medium tracking-tight text-text-primary sm:text-6xl">
          Understand any
          <br />
          <span className="text-accent-default">codebase instantly</span>
        </h1>
        <p className="max-w-[700px] text-lg text-text-secondary">
          Upload a repository and get architecture diagrams, dependency graphs, security
          insights, and an AI copilot that understands your project.
        </p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row">
        <Link to="/upload" onClick={beginUploadFlow}>
          <Button variant="primary" size="lg">
            Upload Repository
          </Button>
        </Link>
        <Button variant="secondary" size="lg">
          View Demo
        </Button>
      </div>
    </div>
  );
}
