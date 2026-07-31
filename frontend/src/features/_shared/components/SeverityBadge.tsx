import { Badge } from '@/design-system/primitives/Badge';
import { severityVariant } from './severity';

export function SeverityBadge({ severity }: { severity: string }) {
  return <Badge variant={severityVariant(severity)}>{severity}</Badge>;
}
