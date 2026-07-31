export function severityVariant(
  severity: string
): 'danger' | 'warning' | 'info' | 'default' | 'success' {
  const value = severity.toLowerCase();
  if (value.includes('critical') || value.includes('high')) return 'danger';
  if (value.includes('medium') || value.includes('major') || value.includes('warning')) {
    return 'warning';
  }
  if (value.includes('low') || value.includes('minor') || value.includes('info')) return 'info';
  if (value.includes('success') || value.includes('healthy')) return 'success';
  return 'default';
}
