import { Link } from 'react-router-dom';
import { UploadPanel } from '@/features/upload';
import { Button } from '@/design-system/primitives/Button';

export default function UploadPage() {
  return (
    <div className="min-h-screen bg-bg-base px-4 py-10">
      <div className="mb-8 flex items-center justify-between">
        <Link to="/" className="text-sm font-medium text-text-primary">
          CodeGraph
        </Link>
        <Link to="/">
          <Button variant="ghost" size="sm">
            Back
          </Button>
        </Link>
      </div>
      <UploadPanel />
    </div>
  );
}
