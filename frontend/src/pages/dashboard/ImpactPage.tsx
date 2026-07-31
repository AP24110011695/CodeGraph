import { useParams } from 'react-router-dom';
import { ImpactPanel } from '@/features/impact-analysis';

export default function ImpactPage() {
  const { repoId } = useParams();

  if (!repoId) {
    return null;
  }

  return <ImpactPanel repoId={repoId} />;
}
