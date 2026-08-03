import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/design-system/primitives/Button';

interface PageNavbarProps {
  onBack?: () => void;
  backHref?: string;
  showBack?: boolean;
}

export function PageNavbar({ onBack, backHref = '/', showBack = true }: PageNavbarProps) {
  const navigate = useNavigate();
  const handleBack = () => {
    if (onBack) {
      onBack();
      return;
    }
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate(backHref, { replace: true });
    }
  };

  return (
    <nav className="sticky top-0 z-50 h-[72px] border-b border-border-subtle bg-bg-base/80 backdrop-blur-sm">
      <div className="mx-auto flex h-full max-w-[1280px] items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-default">
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M8 1L2 4V12L8 15L14 12V4L8 1Z"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M8 8V15"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M8 8L14 4"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M8 8L2 4"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <span className="text-lg font-medium text-text-primary">CodeGraph</span>
        </Link>

        {showBack && (
          <div>
            <Button variant="ghost" size="sm" onClick={handleBack}>
              Back
            </Button>
          </div>
        )}
      </div>
    </nav>
  );
}
