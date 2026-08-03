import { useEffect, useId, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { ChevronDown, FolderGit2, Plus, Trash2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/cn';
import { useRepositoryStore } from '@/core/store/repository.store';
import { Badge } from '@/design-system/primitives/Badge';
import { Button } from '@/design-system/primitives/Button';
import { useRepositoriesQuery, useDeleteRepositoryMutation } from '../api/repositories.queries';
import { isRepositoryReady, type RepositorySummary } from '../api/repositories.types';
import { DeleteRepositoryDialog } from './DeleteRepositoryDialog';
import { beginUploadFlow } from '@/core/navigation/flow-session';

function statusBadgeVariant(status: string): 'success' | 'warning' | 'danger' | 'default' | 'info' {
  const value = status.toUpperCase();
  if (value === 'READY') return 'success';
  if (value === 'FAILED' || value === 'CANCELLED') return 'danger';
  if (value === 'INDEXING' || value === 'UPLOADED' || value === 'QUEUED') return 'warning';
  return 'default';
}

function formatUploadedAt(iso: string): string {
  try {
    return formatDistanceToNow(new Date(iso), { addSuffix: true });
  } catch {
    return iso;
  }
}

export function RepositorySelector() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const menuId = useId();
  const rootRef = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<RepositorySummary | null>(null);

  const activeRepositoryId = useRepositoryStore((s) => s.activeRepositoryId);
  const activeRepository = useRepositoryStore((s) => s.activeRepository);
  const selectRepository = useRepositoryStore((s) => s.selectRepository);
  const clearRepository = useRepositoryStore((s) => s.clearRepository);

  const listQuery = useRepositoriesQuery();
  const deleteMutation = useDeleteRepositoryMutation();

  const repositories = listQuery.data?.repositories ?? [];
  const active =
    repositories.find((r) => r.id === activeRepositoryId) ??
    (activeRepository
      ? {
          id: activeRepository.id,
          name: activeRepository.name,
          uploaded_at: activeRepository.uploadedAt ?? new Date().toISOString(),
          status: 'READY',
          framework: null,
          language: null,
        }
      : null);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false);
    };
    document.addEventListener('mousedown', onPointerDown);
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('mousedown', onPointerDown);
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [open]);

  const switchTo = async (repo: RepositorySummary) => {
    setOpen(false);
    if (repo.id === activeRepositoryId) return;

    selectRepository(repo, { ready: isRepositoryReady(repo.status) });
    await queryClient.invalidateQueries();

    if (isRepositoryReady(repo.status)) {
      navigate(`/dashboard/${repo.id}`);
    } else {
      navigate(`/indexing/${repo.id}`);
    }
  };

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    const deletedId = pendingDelete.id;
    await deleteMutation.mutateAsync(deletedId);
    setPendingDelete(null);
    setOpen(false);

    const remaining = repositories.filter((r) => r.id !== deletedId);
    if (deletedId === activeRepositoryId) {
      clearRepository();
      await queryClient.invalidateQueries();
      if (remaining.length === 0) {
        beginUploadFlow();
        navigate('/upload');
        return;
      }
      const next = remaining.find((r) => isRepositoryReady(r.status)) ?? remaining[0];
      selectRepository(next, { ready: isRepositoryReady(next.status) });
      await queryClient.invalidateQueries();
      navigate(isRepositoryReady(next.status) ? `/dashboard/${next.id}` : `/indexing/${next.id}`);
      return;
    }

    await queryClient.invalidateQueries();
  };

  return (
    <>
      <div ref={rootRef} className="relative min-w-0">
        <button
          type="button"
          className={cn(
            'flex max-w-[min(100%,22rem)] items-center gap-2.5 rounded-lg border border-border-base bg-[#181614] px-3 py-1.5 text-left transition-all duration-normal',
            'hover:border-border-strong hover:bg-[#2A2420] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-default/40'
          )}
          aria-haspopup="listbox"
          aria-expanded={open}
          aria-controls={menuId}
          onClick={() => setOpen((value) => !value)}
        >
          <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-accent-subtle text-accent-default">
            <FolderGit2 className="h-3.5 w-3.5" aria-hidden />
          </div>
          <span className="min-w-0 flex-1 truncate text-sm font-medium text-text-primary">
            {active?.name ?? 'Select repository'}
          </span>
          {active ? (
            <Badge variant={statusBadgeVariant(active.status)} className="shrink-0 text-[10px] uppercase font-semibold">
              {active.status}
            </Badge>
          ) : null}
          <ChevronDown
            className={cn('h-3.5 w-3.5 shrink-0 text-text-tertiary transition-transform duration-normal', open && 'rotate-180')}
            aria-hidden
          />
        </button>

        {open ? (
          <div
            id={menuId}
            role="listbox"
            className="absolute left-0 top-[calc(100%+0.5rem)] z-50 w-[min(100vw-2rem,26rem)] overflow-hidden rounded-2xl border border-border-base bg-[#181614] p-1.5 shadow-2xl backdrop-blur-md"
            style={{ boxShadow: '0 20px 40px rgba(0,0,0,0.6)' }}
          >
            <div className="max-h-80 overflow-auto space-y-1 p-1">
              {listQuery.isLoading ? (
                <p className="px-3 py-4 text-xs text-text-secondary">Loading repositories…</p>
              ) : repositories.length === 0 ? (
                <p className="px-3 py-4 text-xs text-text-secondary">No repositories yet.</p>
              ) : (
                repositories.map((repo) => {
                  const selected = repo.id === activeRepositoryId;
                  return (
                    <div
                      key={repo.id}
                      className={cn(
                        'group flex items-center justify-between rounded-xl px-3 py-2.5 transition-all duration-fast',
                        selected
                          ? 'bg-[rgba(232,160,69,0.12)] border border-accent-muted/30'
                          : 'hover:bg-[#2A2420] hover:translate-x-0.5'
                      )}
                    >
                      <button
                        type="button"
                        role="option"
                        aria-selected={selected}
                        className="min-w-0 flex-1 text-left"
                        onClick={() => void switchTo(repo)}
                      >
                        <div className="flex items-center gap-2.5">
                          <div className={cn(
                            'flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border',
                            selected
                              ? 'border-accent-default/40 bg-accent-subtle text-accent-default'
                              : 'border-border-base bg-[#121110] text-text-tertiary group-hover:text-text-primary'
                          )}>
                            <FolderGit2 className="h-4 w-4" aria-hidden />
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-2">
                              <span className="truncate text-sm font-medium text-text-primary">{repo.name}</span>
                              {selected ? (
                                <span className="rounded bg-accent-default/20 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-accent-default">Active</span>
                              ) : null}
                            </div>
                            <div className="mt-1 flex flex-wrap items-center gap-1.5">
                              <Badge variant={statusBadgeVariant(repo.status)} className="text-[10px] uppercase">
                                {repo.status}
                              </Badge>
                              {repo.language ? (
                                <span className="rounded border border-border-base bg-[#121110] px-1.5 py-0.5 text-[10px] text-text-secondary">
                                  {repo.language}
                                </span>
                              ) : null}
                              {repo.framework ? (
                                <span className="rounded border border-border-base bg-[#121110] px-1.5 py-0.5 text-[10px] text-text-tertiary">
                                  {repo.framework}
                                </span>
                              ) : null}
                              <span className="text-[11px] text-text-tertiary ml-auto">{formatUploadedAt(repo.uploaded_at)}</span>
                            </div>
                          </div>
                        </div>
                      </button>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="ml-2 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity duration-fast h-7 w-7 p-0"
                        aria-label={`Delete ${repo.name}`}
                        onClick={(event) => {
                          event.stopPropagation();
                          setPendingDelete(repo);
                        }}
                      >
                        <Trash2 className="h-3.5 w-3.5 text-danger hover:text-danger/80" />
                      </Button>
                    </div>
                  );
                })
              )}
            </div>
            <div className="mt-1 border-t border-border-base pt-1">
              <button
                type="button"
                className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-xs font-medium text-text-secondary hover:bg-[#2A2420] hover:text-text-primary transition-colors"
                onClick={() => {
                  setOpen(false);
                  beginUploadFlow();
                  navigate('/upload');
                }}
              >
                <Plus className="h-3.5 w-3.5 text-accent-default" aria-hidden />
                Add Repository
              </button>
            </div>
          </div>
        ) : null}
      </div>

      <DeleteRepositoryDialog
        repository={pendingDelete}
        isDeleting={deleteMutation.isPending}
        onCancel={() => setPendingDelete(null)}
        onConfirm={() => void confirmDelete()}
      />
    </>
  );

}
