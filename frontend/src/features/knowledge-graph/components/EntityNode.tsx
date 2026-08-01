import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import {
  Box,
  FileCode2,
  Folder,
  GitBranch,
  Layers,
  Shield,
  Wrench,
  Database,
  Cpu,
  Network,
} from 'lucide-react';
import { cn } from '@/lib/cn';
import { Badge } from '@/design-system/primitives/Badge';
import { languagePaletteColor } from '@/features/_shared/components/graph';

export type EntityNodeData = {
  label: string;
  entityType: string;
  labels: string[];
  incomingCount: number;
  outgoingCount: number;
  highlighted?: boolean;
  dimmed?: boolean;
  pulse?: boolean;
};

function typeColor(type: string): string {
  const key = type.toLowerCase();
  if (key.includes('security') || key.includes('finding') || key.includes('vulnerability')) return 'text-danger';
  if (key.includes('quality') || key.includes('smell') || key.includes('review') || key.includes('debt')) {
    return 'text-warning';
  }
  if (key.includes('module') || key.includes('package') || key.includes('layer') || key.includes('component')) {
    return 'text-accent-default';
  }
  if (key.includes('class') || key.includes('function') || key.includes('method') || key.includes('code')) {
    return 'text-info';
  }
  if (key.includes('database') || key.includes('schema') || key.includes('table')) return 'text-info';
  if (key.includes('service') || key.includes('api') || key.includes('endpoint')) return 'text-warning';
  return 'text-text-secondary';
}

function typeBgColor(type: string): string {
  const key = type.toLowerCase();
  if (key.includes('security') || key.includes('finding') || key.includes('vulnerability')) return 'bg-danger/10 border-danger/30';
  if (key.includes('quality') || key.includes('smell') || key.includes('review') || key.includes('debt')) {
    return 'bg-warning/10 border-warning/30';
  }
  if (key.includes('module') || key.includes('package') || key.includes('layer') || key.includes('component')) {
    return 'bg-accent-subtle border-accent-muted/30';
  }
  if (key.includes('class') || key.includes('function') || key.includes('method') || key.includes('code')) {
    return 'bg-info/10 border-info/30';
  }
  if (key.includes('database') || key.includes('schema') || key.includes('table')) return 'bg-info/10 border-info/30';
  if (key.includes('service') || key.includes('api') || key.includes('endpoint')) return 'bg-warning/10 border-warning/30';
  return 'bg-[#181614] border-border-base';
}

function TypeIcon({ type }: { type: string }) {
  const key = type.toLowerCase();
  if (key.includes('file') || key.includes('code') || key.includes('class') || key.includes('function')) return <FileCode2 className="h-3.5 w-3.5" />;
  if (key.includes('module') || key.includes('package') || key.includes('component')) return <Box className="h-3.5 w-3.5" />;
  if (key.includes('folder') || key.includes('repository') || key.includes('directory')) return <Folder className="h-3.5 w-3.5" />;
  if (key.includes('layer') || key.includes('framework') || key.includes('architecture')) return <Layers className="h-3.5 w-3.5" />;
  if (key.includes('security') || key.includes('finding') || key.includes('vulnerability')) return <Shield className="h-3.5 w-3.5" />;
  if (key.includes('refactor') || key.includes('metric') || key.includes('quality')) return <Wrench className="h-3.5 w-3.5" />;
  if (key.includes('database') || key.includes('schema') || key.includes('table')) return <Database className="h-3.5 w-3.5" />;
  if (key.includes('service') || key.includes('api') || key.includes('endpoint')) return <Cpu className="h-3.5 w-3.5" />;
  if (key.includes('network') || key.includes('connection') || key.includes('relation')) return <Network className="h-3.5 w-3.5" />;
  return <GitBranch className="h-3.5 w-3.5" />;
}

function EntityNodeComponent({ data, selected }: NodeProps) {
  const nodeData = data as EntityNodeData;
  const accent = languagePaletteColor(nodeData.entityType);
  const isActive = selected || nodeData.highlighted;

  return (
    <div
      className={cn(
        'group relative min-w-[200px] max-w-[240px] rounded-2xl border px-3.5 py-3',
        'shadow-[0_10px_28px_rgba(0,0,0,0.4)] transition-all duration-300 ease-out',
        'hover:z-10 hover:scale-[1.02] hover:border-accent-default hover:shadow-[0_16px_36px_rgba(0,0,0,0.5)]',
        typeBgColor(nodeData.entityType),
        isActive &&
          'z-10 scale-[1.02] border-accent-default shadow-[0_0_24px_rgba(232,160,69,0.35)] ring-2 ring-accent-default/40',
        nodeData.dimmed && 'opacity-25',
        nodeData.pulse && 'animate-graph-pulse'
      )}
    >
      <span
        className="absolute left-0 top-3 bottom-3 w-1 rounded-r-full"
        style={{ backgroundColor: accent }}
        aria-hidden
      />
      <Handle
        type="target"
        position={Position.Left}
        className="!h-3 !w-3 !border-2 !border-bg-base !bg-accent-default opacity-0 transition-opacity group-hover:opacity-100"
      />

      <div className="flex items-start gap-2.5">
        <div
          className={cn(
            'mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-xl bg-bg-base/50',
            typeColor(nodeData.entityType)
          )}
        >
          <TypeIcon type={nodeData.entityType} />
        </div>

        <div className="min-w-0 flex-1">
          <p className="truncate text-[13px] font-semibold tracking-tight text-text-primary transition-colors group-hover:text-accent-default">
            {nodeData.label}
          </p>

          <div className="mt-2 flex items-center gap-1.5">
            <Badge
              variant="default"
              className={cn('border px-1.5 py-0 text-[9px] font-medium', typeBgColor(nodeData.entityType))}
            >
              {nodeData.entityType}
            </Badge>

            <div className="ml-auto flex items-center gap-0.5 text-[10px] font-semibold tabular-nums text-text-tertiary">
              <span className="text-accent-default">↓</span>
              {nodeData.outgoingCount}
              <span className="mx-1 text-border-base">·</span>
              <span className="text-info">↑</span>
              {nodeData.incomingCount}
            </div>
          </div>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="!h-3 !w-3 !border-2 !border-bg-base !bg-accent-default opacity-0 transition-opacity group-hover:opacity-100"
      />
    </div>
  );
}

export const EntityNode = memo(EntityNodeComponent);
