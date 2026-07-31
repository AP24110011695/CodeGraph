import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { Boxes } from 'lucide-react';
import { cn } from '@/lib/cn';
import { Badge } from '@/design-system/primitives/Badge';

export type ArchitectureNodeData = {
  label: string;
  moduleType: string;
  layer: string;
  componentCount: number;
  fileCount: number;
  incomingCount: number;
  outgoingCount: number;
};

function layerTone(layer: string): string {
  const key = layer.toLowerCase();
  if (key.includes('presentation') || key.includes('ui') || key.includes('frontend')) {
    return 'border-info/40 bg-info/10';
  }
  if (key.includes('domain') || key.includes('business') || key.includes('service')) {
    return 'border-accent-muted/40 bg-accent-subtle';
  }
  if (key.includes('data') || key.includes('infrastructure') || key.includes('persistence')) {
    return 'border-warning/40 bg-warning/10';
  }
  return 'border-border-base bg-bg-elevated';
}

function ArchitectureNodeComponent({ data, selected }: NodeProps) {
  const nodeData = data as ArchitectureNodeData;

  return (
    <div
      className={cn(
        'min-w-[200px] max-w-[240px] rounded-md border px-3 py-2 shadow-none transition-transform duration-fast',
        layerTone(nodeData.layer),
        selected && 'scale-105 border-accent-default ring-1 ring-accent-default'
      )}
    >
      <Handle type="target" position={Position.Top} className="!h-2 !w-2 !bg-accent-default" />
      <div className="flex items-start gap-2">
        <Boxes className="mt-0.5 h-3.5 w-3.5 shrink-0 text-text-secondary" aria-hidden />
        <div className="min-w-0">
          <p className="truncate text-xs font-medium text-text-primary">{nodeData.label}</p>
          <p className="truncate text-[10px] text-text-tertiary">{nodeData.moduleType}</p>
          <div className="mt-1 flex flex-wrap items-center gap-1">
            <Badge variant="default" className="px-1.5 py-0 text-[10px]">
              {nodeData.layer}
            </Badge>
            <span className="text-[10px] text-text-tertiary">
              {nodeData.componentCount} comp · {nodeData.fileCount} files
            </span>
          </div>
          <p className="mt-0.5 text-[10px] text-text-tertiary">
            ↓{nodeData.outgoingCount} · ↑{nodeData.incomingCount}
          </p>
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} className="!h-2 !w-2 !bg-accent-default" />
    </div>
  );
}

export const ArchitectureNode = memo(ArchitectureNodeComponent);
