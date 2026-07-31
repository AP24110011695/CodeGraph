import { useParams } from 'react-router-dom';
import { PagePlaceholder } from '../_PagePlaceholder';

export default function ReportDetailPage() {
  const { reportId } = useParams();

  return (
    <PagePlaceholder
      title="Report Detail"
      description={`Report ${reportId ?? '—'} detail view will be implemented in Phase 7.`}
    />
  );
}
