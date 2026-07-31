import { AnimatePresence, motion } from 'framer-motion';
import { Button } from '@/design-system/primitives/Button';
import { useUpload } from '../hooks/useUpload';
import { UploadConstraints } from './UploadConstraints';
import { UploadDropzone } from './UploadDropzone';
import { UploadProgressBar } from './UploadProgressBar';

export function UploadPanel() {
  const { startUpload, reset, progress, isUploading, error } = useUpload();

  return (
    <div className="mx-auto flex w-full max-w-xl flex-col gap-6">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-medium text-text-primary">Upload a repository</h1>
        <p className="text-sm text-text-secondary">
          Drop a ZIP of your codebase to begin indexing and architecture analysis.
        </p>
      </div>

      <UploadDropzone
        disabled={isUploading}
        error={error}
        onFileSelected={(file) => {
          void startUpload(file);
        }}
      />

      <AnimatePresence>
        {isUploading && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
          >
            <UploadProgressBar progress={progress} />
          </motion.div>
        )}
      </AnimatePresence>

      {error && (
        <div className="space-y-3 rounded-md border border-danger/30 bg-danger/10 p-4">
          <p className="text-sm text-danger">{error}</p>
          <Button variant="danger" size="sm" onClick={reset}>
            Retry
          </Button>
        </div>
      )}

      <UploadConstraints />
    </div>
  );
}
