import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/cn';

const avatarVariants = cva(
  'relative flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-bg-subtle text-text-secondary',
  {
    variants: {
      size: {
        sm: 'h-6 w-6 text-xs',
        md: 'h-8 w-8 text-sm',
        lg: 'h-10 w-10 text-base',
      },
    },
    defaultVariants: {
      size: 'md',
    },
  }
);

export interface AvatarProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof avatarVariants> {
  src?: string;
  alt?: string;
  fallback?: string;
}

export function Avatar({
  className,
  size,
  src,
  alt = '',
  fallback,
  ...props
}: AvatarProps): React.JSX.Element {
  const [failed, setFailed] = React.useState(false);
  const initials = (fallback ?? alt.slice(0, 2).toUpperCase()) || '?';

  return (
    <div className={cn(avatarVariants({ size }), className)} {...props}>
      {src && !failed ? (
        <img
          src={src}
          alt={alt}
          className="h-full w-full object-cover"
          onError={() => setFailed(true)}
        />
      ) : (
        <span aria-hidden={!alt}>{initials}</span>
      )}
    </div>
  );
}

export { avatarVariants };
