import { motion } from 'framer-motion';

interface UploadProgressBarProps {
  progress: number;
}

export function UploadProgressBar({ progress }: UploadProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, progress));

  return (
    <div className="space-y-2" aria-live="polite">
      <div className="flex items-center justify-between text-xs text-text-secondary">
        <span>Uploading…</span>
        <span>{clamped}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-md bg-bg-subtle">
        <motion.div
          className="h-full rounded-md bg-accent-default"
          initial={{ width: 0 }}
          animate={{ width: `${clamped}%` }}
          transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
        />
      </div>
    </div>
  );
}
