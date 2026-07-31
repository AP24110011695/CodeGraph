import { useParams } from 'react-router-dom';
import { MetricsPanel } from '@/features/metrics';

export default function MetricsPage() {
  const { repoId } = useParams();

  if (!repoId) {
    return null;
  }

  return <MetricsPanel repoId={repoId} />;
}
