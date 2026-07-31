import { useParams } from 'react-router-dom';
import { DashboardOverviewPanel } from '@/features/dashboard';

export default function OverviewPage() {
  const { repoId } = useParams();

  if (!repoId) {
    return null;
  }

  return <DashboardOverviewPanel repoId={repoId} />;
}
