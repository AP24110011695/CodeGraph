import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/cn';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl font-medium transition-all duration-normal active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-default focus-visible:ring-offset-2 focus-visible:ring-offset-bg-base disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary:
          'bg-accent-default text-text-primary shadow-md hover:bg-accent-hover hover:-translate-y-0.5 hover:shadow-lg active:bg-accent-pressed active:translate-y-0',
        secondary:
          'border border-border-base bg-bg-elevated text-text-primary hover:border-border-strong hover:bg-accent-subtle hover:text-accent-default hover:-translate-y-0.5',
        ghost: 'text-text-secondary hover:bg-bg-hover hover:text-text-primary',
        danger: 'border border-danger/30 bg-danger/10 text-danger hover:bg-danger/20 hover:border-danger/50',
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        md: 'h-9 px-4 text-sm',
        lg: 'h-11 px-5 text-base',
      },
    },
    defaultVariants: {
      variant: 'secondary',
      size: 'md',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, type = 'button', ...props }, ref) => {
    return (
      <button
        ref={ref}
        type={type}
        className={cn(buttonVariants({ variant, size }), className)}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';

export { buttonVariants };

