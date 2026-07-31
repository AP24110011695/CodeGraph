import { useParams } from 'react-router-dom';
import { CopilotPanel } from '@/features/copilot';

export default function CopilotPage() {
  const { repoId } = useParams();
  if (!repoId) return null;
  return <CopilotPanel repoId={repoId} />;
}
