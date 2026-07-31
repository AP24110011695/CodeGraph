import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/cn';

const skeletonVariants = cva('animate-skeleton-pulse rounded-md bg-bg-subtle', {
  variants: {
    variant: {
      default: '',
      text: 'h-4 w-full',
      circle: 'rounded-full',
    },
  },
  defaultVariants: {
    variant: 'default',
  },
});

export interface SkeletonProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof skeletonVariants> {}

export function Skeleton({ className, variant, ...props }: SkeletonProps): React.JSX.Element {
  return (
    <div
      aria-hidden
      className={cn(skeletonVariants({ variant }), className)}
      {...props}
    />
  );
}

export { skeletonVariants };
