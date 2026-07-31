import { useParams } from 'react-router-dom';
import { IndexingPanel } from '@/features/indexing';

export default function IndexingPage() {
  const { repoId } = useParams();

  if (!repoId) {
    return null;
  }

  return (
    <div className="min-h-screen bg-bg-base">
      <IndexingPanel repoId={repoId} />
    </div>
  );
}
