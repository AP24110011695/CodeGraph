import { useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import { cn } from '@/lib/cn';
import {
  useNotificationStore,
  type NotificationTone,
} from '@/core/store/notification.store';
import { Button } from '@/design-system/primitives/Button';

const toneClasses: Record<NotificationTone, string> = {
  info: 'border-info/30 bg-bg-elevated text-text-primary',
  success: 'border-success/30 bg-bg-elevated text-text-primary',
  warning: 'border-warning/30 bg-bg-elevated text-text-primary',
  danger: 'border-danger/30 bg-bg-elevated text-text-primary',
};

const accentBar: Record<NotificationTone, string> = {
  info: 'bg-info',
  success: 'bg-success',
  warning: 'bg-warning',
  danger: 'bg-danger',
};

export function ToastContainer() {
  const queue = useNotificationStore((s) => s.queue);
  const removeNotification = useNotificationStore((s) => s.removeNotification);

  useEffect(() => {
    if (queue.length === 0) return;
    const timers = queue.map((item) =>
      window.setTimeout(() => removeNotification(item.id), 4000)
    );
    return () => {
      timers.forEach((timer) => window.clearTimeout(timer));
    };
  }, [queue, removeNotification]);

  return (
    <div
      className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-full max-w-sm flex-col gap-2 p-2"
      aria-live="polite"
      aria-relevant="additions"
    >
      <AnimatePresence initial={false}>
        {queue.map((item) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 12, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.98 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className={cn(
              'pointer-events-auto relative overflow-hidden rounded-md border shadow-none',
              toneClasses[item.tone]
            )}
            role="status"
          >
            <div className={cn('absolute inset-y-0 left-0 w-1', accentBar[item.tone])} />
            <div className="flex items-start gap-3 px-4 py-3 pl-5">
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium">{item.title}</p>
                {item.description && (
                  <p className="mt-0.5 text-xs text-text-secondary">{item.description}</p>
                )}
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 shrink-0 px-0"
                aria-label="Dismiss notification"
                onClick={() => removeNotification(item.id)}
              >
                <X className="h-3.5 w-3.5" />
              </Button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
