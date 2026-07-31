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
        'flex cursor-pointer flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border-strong bg-bg-elevated px-6 py-16 text-center transition-colors duration-fast',
        dragging && 'border-accent-default bg-accent-subtle',
        error && 'border-danger/50 bg-danger/5',
        disabled && 'pointer-events-none opacity-60'
      )}
    >
      <UploadCloud className={cn('h-8 w-8', error ? 'text-danger' : 'text-accent-default')} />
      <div className="space-y-1">
        <p className="text-base text-text-primary">Drag and drop a ZIP archive</p>
        <p className="text-sm text-text-secondary">or click to browse your files</p>
      </div>
      {selectedName && !error && (
        <p className="text-xs text-text-tertiary">{selectedName}</p>
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
