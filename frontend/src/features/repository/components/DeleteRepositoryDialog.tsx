import { Button } from '@/design-system/primitives/Button';
import type { RepositorySummary } from '../api/repositories.types';

interface DeleteRepositoryDialogProps {
  repository: RepositorySummary | null;
  isDeleting: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

export function DeleteRepositoryDialog({
  repository,
  isDeleting,
  onCancel,
  onConfirm,
}: DeleteRepositoryDialogProps) {
  if (!repository) return null;

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 p-4"
      role="presentation"
      onClick={onCancel}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-repo-title"
        className="w-full max-w-md rounded-lg border border-border-base bg-bg-elevated p-5 shadow-lg"
        onClick={(event) => event.stopPropagation()}
      >
        <h2 id="delete-repo-title" className="text-base font-medium text-text-primary">
          Delete repository?
        </h2>
        <p className="mt-2 text-sm text-text-secondary">
          This permanently removes <span className="font-medium text-text-primary">{repository.name}</span> and
          its indexed data. This action cannot be undone.
        </p>
        <div className="mt-5 flex justify-end gap-2">
          <Button variant="secondary" size="sm" onClick={onCancel} disabled={isDeleting}>
            Cancel
          </Button>
          <Button variant="danger" size="sm" onClick={onConfirm} disabled={isDeleting}>
            {isDeleting ? 'Deleting…' : 'Delete Repository'}
          </Button>
        </div>
      </div>
    </div>
  );
}
