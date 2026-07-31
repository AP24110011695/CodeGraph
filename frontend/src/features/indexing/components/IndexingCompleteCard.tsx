import { Link } from 'react-router-dom';
import { Button } from '@/design-system/primitives/Button';

interface IndexingCompleteCardProps {
  repoId: string;
}

export function IndexingCompleteCard({ repoId }: IndexingCompleteCardProps) {
  return (
    <div className="rounded-md border border-success/30 bg-success/10 p-4">
      <h2 className="text-sm font-medium text-text-primary">Indexing complete</h2>
      <p className="mt-1 text-sm text-text-secondary">
        Your repository is ready. Open the dashboard to explore architecture, risks, and insights.
      </p>
      <div className="mt-4">
        <Link to={`/dashboard/${repoId}`}>
          <Button variant="primary">Open Dashboard</Button>
        </Link>
      </div>
    </div>
  );
}
