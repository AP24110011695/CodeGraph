import { format, formatDistanceToNow } from 'date-fns';

export function formatDate(value: Date | string | number): string {
  return format(new Date(value), 'MMM d, yyyy');
}

export function formatRelative(value: Date | string | number): string {
  return formatDistanceToNow(new Date(value), { addSuffix: true });
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'] as const;
  const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const size = bytes / 1024 ** exponent;
  return `${size.toFixed(exponent === 0 ? 0 : 1)} ${units[exponent]}`;
}
