import { MAX_ZIP_BYTES } from '../api/upload.types';
import { formatFileSize } from '@/lib/format';

export function UploadConstraints() {
  return (
    <ul className="space-y-1 text-xs text-text-tertiary">
      <li>Supported format: `.zip` archives only</li>
      <li>Maximum size: {formatFileSize(MAX_ZIP_BYTES)}</li>
      <li>GitHub URL import is not available yet — use a local ZIP export</li>
    </ul>
  );
}
