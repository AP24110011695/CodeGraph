import { useParams } from 'react-router-dom';
import { ReportsPanel } from '@/features/reports';

export default function ReportsPage() {
  const { repoId } = useParams();
  if (!repoId) return null;
  return <ReportsPanel repoId={repoId} />;
}
