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
  highlighted?: boolean;
  dimmed?: boolean;
  pulse?: boolean;
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
  return 'border-border-base bg-[#181614]';
}

function ArchitectureNodeComponent({ data, selected }: NodeProps) {
  const nodeData = data as ArchitectureNodeData;
  const isActive = selected || nodeData.highlighted;

  return (
    <div
      className={cn(
        'group relative min-w-[220px] max-w-[260px] rounded-2xl border px-4 py-3.5',
        'shadow-[0_10px_28px_rgba(0,0,0,0.4)] transition-all duration-300 ease-out',
        'hover:z-10 hover:scale-[1.02] hover:border-accent-default hover:shadow-[0_16px_36px_rgba(0,0,0,0.5)]',
        layerTone(nodeData.layer),
        isActive &&
          'z-10 scale-[1.02] border-accent-default shadow-[0_0_24px_rgba(232,160,69,0.35)] ring-2 ring-accent-default/40',
        nodeData.dimmed && 'opacity-25',
        nodeData.pulse && 'animate-graph-pulse'
      )}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!h-3 !w-3 !border-2 !border-[#0F0E0D] !bg-accent-default opacity-0 transition-opacity group-hover:opacity-100"
      />
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-border-base bg-[#121110] text-text-secondary shadow-inner">
          <Boxes className="h-4 w-4" aria-hidden />
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate text-[13px] font-semibold tracking-tight text-text-primary transition-colors group-hover:text-accent-default">
            {nodeData.label}
          </p>
          <p className="mt-0.5 truncate text-[10px] text-text-tertiary">{nodeData.moduleType}</p>
          <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
            <Badge variant="default" className="px-1.5 py-0 text-[10px]">
              {nodeData.layer}
            </Badge>
            <span className="text-[10px] text-text-tertiary">
              {nodeData.componentCount} comp · {nodeData.fileCount} files
            </span>
            <span className="ml-auto text-[10px] font-semibold tabular-nums text-text-tertiary">
              <span className="text-accent-default">↓</span>
              {nodeData.outgoingCount}
              <span className="mx-1 text-border-base">·</span>
              <span className="text-info">↑</span>
              {nodeData.incomingCount}
            </span>
          </div>
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        className="!h-3 !w-3 !border-2 !border-[#0F0E0D] !bg-accent-default opacity-0 transition-opacity group-hover:opacity-100"
      />
    </div>
  );
}

export const ArchitectureNode = memo(ArchitectureNodeComponent);
