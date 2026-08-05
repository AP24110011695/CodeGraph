import { Link } from 'react-router-dom';
import {
  GitBranch,
  Bot,
  FileText,
  Layers,
  ShieldAlert,
  Search,
} from 'lucide-react';

interface QuickActionGridProps {
  repoId: string;
}

const actions = [
  { to: 'graph', label: 'Dependency Graph', icon: GitBranch },
  { to: 'architecture', label: 'Architecture', icon: Layers },
  { to: 'copilot', label: 'Copilot', icon: Bot },
  { to: 'reports', label: 'Reports', icon: FileText },
  { to: 'security', label: 'Security', icon: ShieldAlert },
  { to: 'search', label: 'Search', icon: Search },
] as const;

export function QuickActionGrid({ repoId }: QuickActionGridProps) {
  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <h2 className="mb-3 text-sm font-medium text-text-primary">Quick navigation</h2>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <Link
              key={action.to}
              to={`/dashboard/${repoId}/${action.to}`}
              className="flex items-center gap-3 rounded-md border border-border-base bg-bg-base px-3 py-3 text-sm text-text-secondary transition-colors duration-fast hover:border-border-strong hover:bg-bg-subtle hover:text-text-primary"
            >
              <Icon className="h-4 w-4 text-accent-default" aria-hidden />
              {action.label}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
