import { useParams } from 'react-router-dom';
import { DashboardOverviewPanel } from '@/features/dashboard/components/new-dashboard/DashboardOverviewPanel';

export default function OverviewPage() {
  const { repoId } = useParams();

  if (!repoId) {
    return null;
  }

  return <DashboardOverviewPanel repoId={repoId} />;
}
