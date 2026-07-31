import { useParams } from 'react-router-dom';
import { SecurityPanel } from '@/features/security';

export default function SecurityPage() {
  const { repoId } = useParams();

  if (!repoId) {
    return null;
  }

  return <SecurityPanel repoId={repoId} />;
}
