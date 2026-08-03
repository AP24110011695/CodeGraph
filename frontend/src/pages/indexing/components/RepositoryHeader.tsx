import { Badge } from '@/design-system/primitives/Badge';

interface RepositoryHeaderProps {
  repositoryName: string;
  progress: number;
  currentStage: string;
  languages?: string[];
  fileCount?: number;
  folderCount?: number;
  size?: string;
  estimatedTime?: string;
}

export function RepositoryHeader({
  repositoryName,
  progress,
  currentStage,
  languages,
  fileCount,
  folderCount,
  size,
  estimatedTime,
}: RepositoryHeaderProps) {
  return (
    <div className="rounded-xl border border-border-subtle bg-bg-elevated p-6">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-border-subtle bg-bg-subtle text-accent-default">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 7V17C3 17.5304 3.21071 18.0391 3.58579 18.4142C3.96086 18.7893 4.46957 19 5 19H19C19.5304 19 20.0391 18.7893 20.4142 18.4142C20.7893 18.0391 21 17.5304 21 17V7C21 6.46957 20.7893 5.96086 20.4142 5.58579C20.0391 5.21071 19.5304 5 19 5H5C4.46957 5 3.96086 5.21071 3.58579 5.58579C3.21071 5.96086 3 6.46957 3 7Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M3 10H21" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div className="space-y-2">
            <h1 className="text-xl font-medium text-text-primary">{repositoryName}</h1>
            {languages && languages.length > 0 && (
              <div className="flex flex-wrap items-center gap-2">
                {languages.map((lang) => (
                  <Badge key={lang} variant="accent" className="text-xs">
                    {lang}
                  </Badge>
                ))}
              </div>
            )}
            <div className="flex flex-wrap gap-4 text-sm text-text-secondary">
              {fileCount !== undefined && <span>{fileCount} files</span>}
              {folderCount !== undefined && <span>{folderCount} folders</span>}
              {size !== undefined && <span>{size}</span>}
            </div>
          </div>
        </div>

        <div className="text-right">
          <div className="text-3xl font-medium text-accent-default">{progress}%</div>
          {estimatedTime && (
            <div className="text-sm text-text-secondary">{estimatedTime} remaining</div>
          )}
        </div>
      </div>

      <div className="space-y-2">
        <div className="relative h-2 overflow-hidden rounded-full bg-bg-subtle">
          <div
            className="h-full rounded-full bg-accent-default transition-all duration-normal"
            style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
          />
        </div>
        <div className="text-xs text-text-secondary">{currentStage}</div>
      </div>
    </div>
  );
}
