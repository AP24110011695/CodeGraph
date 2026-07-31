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
} from 'lucide-react';
import { cn } from '@/lib/cn';
import { Badge } from '@/design-system/primitives/Badge';

export type EntityNodeData = {
  label: string;
  entityType: string;
  labels: string[];
  incomingCount: number;
  outgoingCount: number;
};

function typeTone(type: string): string {
  const key = type.toLowerCase();
  if (key.includes('security') || key.includes('finding')) return 'border-danger/40 bg-danger/10';
  if (key.includes('quality') || key.includes('smell') || key.includes('review')) {
    return 'border-warning/40 bg-warning/10';
  }
  if (key.includes('module') || key.includes('package') || key.includes('layer')) {
    return 'border-accent-muted/40 bg-accent-subtle';
  }
  if (key.includes('class') || key.includes('function') || key.includes('method')) {
    return 'border-info/40 bg-info/10';
  }
  return 'border-border-base bg-bg-elevated';
}

function TypeIcon({ type }: { type: string }) {
  const key = type.toLowerCase();
  if (key.includes('file')) return <FileCode2 className="h-3.5 w-3.5" />;
  if (key.includes('module') || key.includes('package')) return <Box className="h-3.5 w-3.5" />;
  if (key.includes('folder') || key.includes('repository')) return <Folder className="h-3.5 w-3.5" />;
  if (key.includes('layer') || key.includes('framework')) return <Layers className="h-3.5 w-3.5" />;
  if (key.includes('security')) return <Shield className="h-3.5 w-3.5" />;
  if (key.includes('refactor') || key.includes('metric')) return <Wrench className="h-3.5 w-3.5" />;
  return <GitBranch className="h-3.5 w-3.5" />;
}

function EntityNodeComponent({ data, selected }: NodeProps) {
  const nodeData = data as EntityNodeData;

  return (
    <div
      className={cn(
        'min-w-[160px] max-w-[200px] rounded-md border px-2.5 py-2 shadow-none transition-transform duration-fast',
        typeTone(nodeData.entityType),
        selected && 'scale-105 border-accent-default ring-1 ring-accent-default'
      )}
    >
      <Handle type="target" position={Position.Left} className="!h-2 !w-2 !bg-accent-default" />
      <div className="flex items-start gap-2">
        <span className="mt-0.5 shrink-0 text-text-secondary">
          <TypeIcon type={nodeData.entityType} />
        </span>
        <div className="min-w-0">
          <p className="truncate text-xs font-medium text-text-primary">{nodeData.label}</p>
          <Badge variant="default" className="mt-1 px-1.5 py-0 text-[10px]">
            {nodeData.entityType}
          </Badge>
          <p className="mt-0.5 text-[10px] text-text-tertiary">
            →{nodeData.outgoingCount} · ←{nodeData.incomingCount}
          </p>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="!h-2 !w-2 !bg-accent-default" />
    </div>
  );
}

export const EntityNode = memo(EntityNodeComponent);
