import { Link } from 'react-router-dom';
import { UploadPanel } from '@/features/upload';
import { Button } from '@/design-system/primitives/Button';

export default function UploadPage() {
  return (
    <div className="relative min-h-screen bg-[#0F0E0D] px-4 py-10 overflow-hidden">
      {/* Extremely subtle amber particle gradient near the bottom */}
      <div className="pointer-events-none absolute bottom-0 left-1/2 -translate-x-1/2 h-[450px] w-[800px] rounded-full bg-[radial-gradient(ellipse_at_bottom,rgba(232,160,69,0.07)_0%,rgba(15,14,13,0)_70%)] blur-3xl" />
      
      <div className="relative z-10 mx-auto max-w-5xl">
        <div className="mb-12 flex items-center justify-between">
          <Link to="/" className="text-base font-semibold text-text-primary tracking-tight">
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
    </div>
  );
}

