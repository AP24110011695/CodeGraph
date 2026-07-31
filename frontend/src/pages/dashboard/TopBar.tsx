import { Link, useParams } from 'react-router-dom';
import { Bell, Search, Settings } from 'lucide-react';
import { useRepositoryStore } from '@/core/store/repository.store';
import { Badge } from '@/design-system/primitives/Badge';
import { Avatar } from '@/design-system/primitives/Avatar';
import { Button } from '@/design-system/primitives/Button';
import { Separator } from '@/design-system/primitives/Separator';

export function TopBar() {
  const { repoId } = useParams();
  const activeRepository = useRepositoryStore((s) => s.activeRepository);
  const indexingStatus = useRepositoryStore((s) => s.indexingStatus);
  const name = activeRepository?.name ?? repoId ?? 'Repository';

  return (
    <header className="flex h-12 shrink-0 items-center gap-4 border-b border-border-base bg-bg-elevated px-4">
      <div className="flex min-w-0 flex-1 items-center gap-3">
        <Link to="/" className="shrink-0 text-sm font-medium text-text-primary">
          CodeGraph
        </Link>
        <Separator orientation="vertical" className="h-4" />
        <div className="flex min-w-0 items-center gap-2">
          <span className="truncate text-sm text-text-secondary">{name}</span>
          <Badge variant={indexingStatus === 'ready' ? 'success' : 'default'}>
            {indexingStatus}
          </Badge>
        </div>
      </div>

      {repoId ? (
        <Link
          to={`/dashboard/${repoId}/search`}
          className="hidden md:inline-flex"
          aria-label="Open search"
        >
          <Button
            variant="secondary"
            size="sm"
            className="min-w-[240px] justify-start text-text-tertiary"
          >
            <Search className="h-3.5 w-3.5" />
            <span>Search</span>
            <span className="ml-auto text-xs text-text-tertiary">⌘K</span>
          </Button>
        </Link>
      ) : null}

      <div className="flex items-center gap-1">
        <Button variant="ghost" size="sm" aria-label="Notifications">
          <Bell className="h-4 w-4" />
        </Button>
        <Link to="settings">
          <Button variant="ghost" size="sm" aria-label="Settings">
            <Settings className="h-4 w-4" />
          </Button>
        </Link>
        <Avatar size="sm" fallback="CG" alt="User" className="ml-1" />
      </div>
    </header>
  );
}
