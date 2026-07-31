import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { FileCode2 } from 'lucide-react';
import { cn } from '@/lib/cn';
import { Badge } from '@/design-system/primitives/Badge';

export type DependencyNodeData = {
  label: string;
  path: string;
  language: string;
  dependencyCount: number;
  dependentCount: number;
  selected?: boolean;
};

function languageTone(language: string): string {
  const key = language.toLowerCase();
  if (key.includes('python')) return 'border-warning/40 bg-warning/10';
  if (key.includes('typescript') || key.includes('javascript')) return 'border-info/40 bg-info/10';
  if (key.includes('css') || key.includes('scss')) return 'border-accent-muted/40 bg-accent-subtle';
  return 'border-border-base bg-bg-elevated';
}

function DependencyNodeComponent({ data, selected }: NodeProps) {
  const nodeData = data as DependencyNodeData;

  return (
    <div
      className={cn(
        'min-w-[180px] max-w-[220px] rounded-md border px-3 py-2 shadow-none transition-transform duration-fast',
        languageTone(nodeData.language),
        selected && 'scale-105 border-accent-default ring-1 ring-accent-default'
      )}
    >
      <Handle type="target" position={Position.Left} className="!h-2 !w-2 !bg-accent-default" />
      <div className="flex items-start gap-2">
        <FileCode2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-text-secondary" aria-hidden />
        <div className="min-w-0">
          <p className="truncate text-xs font-medium text-text-primary">{nodeData.label}</p>
          <p className="truncate text-[10px] text-text-tertiary">{nodeData.path}</p>
          <div className="mt-1 flex items-center gap-1">
            <Badge variant="default" className="px-1.5 py-0 text-[10px]">
              {nodeData.language}
            </Badge>
            <span className="text-[10px] text-text-tertiary">
              →{nodeData.dependencyCount} · ←{nodeData.dependentCount}
            </span>
          </div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!h-2 !w-2 !bg-accent-default" />
    </div>
  );
}

export const DependencyNode = memo(DependencyNodeComponent);
