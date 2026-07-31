import { Badge } from '@/design-system/primitives/Badge';
import { cn } from '@/lib/cn';
import { useArchitectureStore } from '../store/architecture.store';

interface ArchitectureLayersProps {
  layers: string[];
  moduleCounts: Record<string, number>;
}

export function ArchitectureLayers({ layers, moduleCounts }: ArchitectureLayersProps) {
  const selectedModuleName = useArchitectureStore((s) => s.selectedModuleName);
  const setSelectedModuleName = useArchitectureStore((s) => s.setSelectedModuleName);

  if (layers.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-border-base bg-bg-elevated px-4 py-2">
      <span className="text-xs font-medium text-text-secondary">Layers</span>
      {layers.map((layer) => (
        <Badge
          key={layer}
          variant="default"
          className={cn('cursor-default', selectedModuleName && 'opacity-80')}
        >
          {layer}
          <span className="ml-1 text-text-tertiary">({moduleCounts[layer] ?? 0})</span>
        </Badge>
      ))}
      {selectedModuleName && (
        <button
          type="button"
          className="ml-auto text-xs text-accent-default hover:underline"
          onClick={() => setSelectedModuleName(null)}
        >
          Clear selection
        </button>
      )}
    </div>
  );
}
