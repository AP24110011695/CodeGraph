import { useParams } from 'react-router-dom';
import { ReportsPanel } from '@/features/reports';

export default function ReportDetailPage() {
  const { repoId, reportId } = useParams();
  if (!repoId || !reportId) return null;
  return <ReportsPanel repoId={repoId} reportId={reportId} />;
}
