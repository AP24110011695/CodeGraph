import { useParams } from 'react-router-dom';
import { TimelinePanel } from '@/features/timeline';

export default function TimelinePage() {
  const { repoId } = useParams();
  if (!repoId) return null;
  return <TimelinePanel repoId={repoId} />;
}
