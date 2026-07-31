import { Skeleton } from '@/design-system/primitives/Skeleton';

export function RouteFallback() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-bg-base p-6">
      <div className="w-full max-w-md space-y-3" aria-live="polite" aria-busy="true">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-2/3" />
      </div>
    </div>
  );
}
