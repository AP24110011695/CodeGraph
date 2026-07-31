import { useParams } from 'react-router-dom';
import { QualityPanel } from '@/features/quality';

export default function QualityPage() {
  const { repoId } = useParams();

  if (!repoId) {
    return null;
  }

  return <QualityPanel repoId={repoId} />;
}
