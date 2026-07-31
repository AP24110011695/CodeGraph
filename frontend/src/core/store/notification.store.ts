import { create } from 'zustand';

export type NotificationTone = 'info' | 'success' | 'warning' | 'danger';

export interface Notification {
  id: string;
  title: string;
  description?: string;
  tone: NotificationTone;
  createdAt: string;
}

interface NotificationState {
  queue: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'createdAt'> & { id?: string }) => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  queue: [],
  addNotification: (notification) =>
    set((state) => ({
      queue: [
        ...state.queue,
        {
          id: notification.id ?? crypto.randomUUID(),
          title: notification.title,
          description: notification.description,
          tone: notification.tone,
          createdAt: new Date().toISOString(),
        },
      ],
    })),
  removeNotification: (id) =>
    set((state) => ({
      queue: state.queue.filter((item) => item.id !== id),
    })),
  clearAll: () => set({ queue: [] }),
}));
