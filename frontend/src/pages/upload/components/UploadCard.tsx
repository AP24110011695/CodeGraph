import { useCallback, useRef, useState, type DragEvent, type ChangeEvent } from 'react';
import { cn } from '@/lib/cn';
import { formatFileSize } from '@/lib/format';
import { validateZipFile } from '@/features/upload/api/upload.types';

interface UploadCardProps {
  disabled?: boolean;
  error?: string | null;
  onFileSelected: (file: File) => void;
}

export function UploadCard({ disabled, error, onFileSelected }: UploadCardProps) {
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
    <div
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
      className={cn(
        'relative flex cursor-pointer flex-col items-center justify-center gap-4 rounded-xl border-2 border-dashed border-border-subtle bg-bg-elevated px-8 py-16 text-center transition-all duration-normal',
        'hover:border-accent-default hover:bg-bg-hover',
        dragging && 'border-accent-default bg-accent-subtle/30',
        error && 'border-danger/50 bg-danger/5',
        disabled && 'pointer-events-none opacity-60'
      )}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-accent-subtle text-accent-default">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M17 8L12 3L7 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M12 3V15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>

      <div className="space-y-1">
        <p className="text-base font-medium text-text-primary">Drop ZIP archive here</p>
        <p className="text-sm text-text-secondary">or click to browse files</p>
      </div>

      {selectedName && !error && (
        <span className="rounded-full border border-accent-muted/40 bg-accent-subtle px-3 py-1 text-xs font-medium text-accent-default">
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
    </div>
  );
}
