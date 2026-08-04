import { useParams } from 'react-router-dom';

export default function OverviewPage() {
  const { repoId } = useParams();

  if (!repoId) {
    return null;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Overview</h1>
      <p className="text-gray-600">Repository ID: {repoId}</p>
    </div>
  );
}
