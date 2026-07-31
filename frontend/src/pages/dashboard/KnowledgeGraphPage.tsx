import { useParams } from 'react-router-dom';
import { KnowledgeGraphPanel } from '@/features/knowledge-graph';

export default function KnowledgeGraphPage() {
  const { repoId } = useParams();
  if (!repoId) return null;
  return <KnowledgeGraphPanel repoId={repoId} />;
}
