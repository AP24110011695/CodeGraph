import { useParams } from 'react-router-dom';
import { DependencyGraphPanel } from '@/features/dependency-graph';

export default function DependencyGraphPage() {
  const { repoId } = useParams();
  if (!repoId) return null;
  return <DependencyGraphPanel repoId={repoId} />;
}
