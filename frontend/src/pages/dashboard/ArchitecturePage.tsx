import { useParams } from 'react-router-dom';
import { ArchitecturePanel } from '@/features/architecture';

export default function ArchitecturePage() {
  const { repoId } = useParams();
  if (!repoId) return null;
  return <ArchitecturePanel repoId={repoId} />;
}
