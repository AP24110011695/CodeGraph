import { useCallback, useRef, useState, type DragEvent, type ChangeEvent } from 'react';
import { motion } from 'framer-motion';
import { UploadCloud } from 'lucide-react';
import { cn } from '@/lib/cn';
import { formatFileSize } from '@/lib/format';
import { validateZipFile } from '../api/upload.types';

interface UploadDropzoneProps {
  disabled?: boolean;
  error?: string | null;
  onFileSelected: (file: File) => void;
}

export function UploadDropzone({ disabled, error, onFileSelected }: UploadDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [selectedName, setSelectedName] = useState<string | null>(null);

  const acceptFile = useCallback(
    (file: File | undefined) => {
      if (!file || disabled) return;
      const validationError = validateZipFile(file);
      if (validationError) {
        setSelectedName(null);
        onFileSelected(file);
        return;
      }
      setSelectedName(`${file.name} · ${formatFileSize(file.size)}`);
      onFileSelected(file);
    },
    [disabled, onFileSelected]
  );

  const onDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragging(false);
    acceptFile(event.dataTransfer.files?.[0]);
  };

  const onChange = (event: ChangeEvent<HTMLInputElement>) => {
    acceptFile(event.target.files?.[0]);
    event.target.value = '';
  };

  return (
    <motion.div
      role="button"
      tabIndex={0}
      aria-disabled={disabled}
      onKeyDown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          inputRef.current?.click();
        }
      }}
      onClick={() => !disabled && inputRef.current?.click()}
      onDragEnter={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={(e) => {
        e.preventDefault();
        setDragging(false);
      }}
      onDrop={onDrop}
      animate={dragging ? { scale: 1.01 } : { scale: 1 }}
      transition={{ duration: 0.15 }}
      className={cn(
        'relative flex cursor-pointer flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed border-[#4A3D33] bg-[#181614] px-8 py-20 text-center transition-all duration-normal shadow-2xl overflow-hidden',
        'hover:border-accent-default hover:bg-[#1D1A17]',
        dragging && 'border-accent-default bg-accent-subtle/30 ring-4 ring-accent-default/20',
        error && 'border-danger/50 bg-danger/5',
        disabled && 'pointer-events-none opacity-60'
      )}
    >
      {dragging && (
        <div className="absolute inset-0 bg-gradient-to-t from-accent-default/10 via-transparent to-transparent animate-pulse pointer-events-none" />
      )}
      <motion.div
        animate={{ y: [0, -6, 0] }}
        transition={{ repeat: Infinity, duration: 3, ease: 'easeInOut' }}
        className="flex h-14 w-14 items-center justify-center rounded-2xl border border-border-base bg-[#121110] shadow-md"
      >
        <UploadCloud className={cn('h-7 w-7', error ? 'text-danger' : 'text-accent-default')} />
      </motion.div>

      <div className="space-y-1 z-10">
        <p className="text-base font-semibold text-text-primary">Drag and drop a ZIP archive</p>
        <p className="text-xs text-text-secondary">or click to browse your local filesystem</p>
      </div>

      {selectedName && !error && (
        <span className="z-10 rounded-full border border-accent-muted/40 bg-accent-subtle px-3 py-1 text-xs font-medium text-accent-default">
          {selectedName}
        </span>
      )}

      <input
        ref={inputRef}
        type="file"
        accept=".zip,application/zip"
        className="hidden"
        disabled={disabled}
        onChange={onChange}
      />
    </motion.div>
  );

}
