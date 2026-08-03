import { useState } from 'react';
import { Button } from '@/design-system/primitives/Button';
import { Input } from '@/design-system/primitives/Input';

export function GitHubImport() {
  const [repoUrl, setRepoUrl] = useState('');

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div className="h-px flex-1 bg-border-subtle" />
        <span className="text-sm text-text-secondary">or analyze from GitHub</span>
        <div className="h-px flex-1 bg-border-subtle" />
      </div>

      <div className="flex items-center gap-3 rounded-xl border border-border-subtle bg-bg-elevated p-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-subtle text-accent-default">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 0C3.58 0 0 3.58 0 8C0 11.54 2.29 14.53 5.47 15.46C5.87 15.53 6.01 15.3 6.01 15.09C6.01 14.9 6 14.33 6 13.69C3.73 14.2 3.26 12.63 3.26 12.63C2.89 11.7 2.36 11.46 2.36 11.46C1.63 10.94 2.42 10.95 2.42 10.95C3.23 11.01 3.65 11.78 3.65 11.78C4.37 12.99 5.52 12.61 6.03 12.38C6.1 11.88 6.33 11.54 6.58 11.33C4.79 11.12 2.91 10.45 2.91 7.45C2.91 6.55 3.23 5.81 3.75 5.23C3.67 5.02 3.39 4.17 3.83 3.02C3.83 3.02 4.53 2.8 6 3.88C6.66 3.69 7.36 3.59 8.06 3.59C8.76 3.59 9.46 3.69 10.12 3.88C11.59 2.8 12.29 3.02 12.29 3.02C12.73 4.17 12.45 5.02 12.37 5.23C12.89 5.81 13.21 6.55 13.21 7.45C13.21 10.46 11.32 11.12 9.52 11.33C9.83 11.58 10.11 12.07 10.11 12.83C10.11 13.95 10.1 14.85 10.1 15.09C10.1 15.3 10.24 15.54 10.64 15.46C13.82 14.53 16.11 11.54 16.11 8C16.11 3.58 12.53 0 8 0Z"/>
          </svg>
        </div>
        <Input
          placeholder="https://github.com/owner/repo"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          className="flex-1"
        />
        <Button variant="primary" size="md" disabled={!repoUrl}>
          Analyze
        </Button>
      </div>
    </div>
  );
}
