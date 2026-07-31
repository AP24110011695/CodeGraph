import { useParams } from 'react-router-dom';
import { SearchPanel } from '@/features/search';

export default function SearchPage() {
  const { repoId } = useParams();
  if (!repoId) return null;
  return <SearchPanel repoId={repoId} />;
}
