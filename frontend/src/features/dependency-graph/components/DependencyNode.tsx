import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { FileCode2, Layers } from 'lucide-react';
import { cn } from '@/lib/cn';
import { languagePaletteColor } from '@/features/_shared/components/graph';

export type DependencyNodeData = {
  label: string;
  path: string;
  language: string;
  dependencyCount: number;
  dependentCount: number;
  selected?: boolean;
  highlighted?: boolean;
  dimmed?: boolean;
  pulse?: boolean;
};

function languageTextClass(language: string): string {
  const key = language.toLowerCase();
  if (key.includes('python')) return 'text-[#E8A045]';
  if (key.includes('typescript') || key.includes('javascript')) return 'text-[#4F9DFF]';
  if (key.includes('css') || key.includes('scss')) return 'text-[#4F9DFF]';
  if (key.includes('rust')) return 'text-[#F28C28]';
  if (key.includes('go')) return 'text-[#27C6B7]';
  if (key.includes('java')) return 'text-[#FF5C5C]';
  return 'text-text-secondary';
}

function getIcon(path: string) {
  const normalized = path.replace(/\\/g, '/').toLowerCase();
  if (normalized.includes('component') || normalized.includes('ui') || normalized.includes('view')) {
    return Layers;
  }
  return FileCode2;
}

function DependencyNodeComponent({ data, selected }: NodeProps) {
  const nodeData = data as DependencyNodeData;
  const Icon = getIcon(nodeData.path);
  const accent = languagePaletteColor(nodeData.language);
  const isActive = selected || nodeData.highlighted;

  return (
    <div
      className={cn(
        'group relative min-w-[220px] max-w-[260px] rounded-2xl border border-border-base bg-[#181614] px-4 py-3.5',
        'shadow-[0_10px_28px_rgba(0,0,0,0.4)] transition-all duration-300 ease-out',
        'hover:z-10 hover:scale-[1.02] hover:border-accent-default hover:shadow-[0_16px_36px_rgba(0,0,0,0.5)]',
        isActive &&
          'z-10 scale-[1.02] border-accent-default bg-[#1D1A17] shadow-[0_0_24px_rgba(232,160,69,0.35)] ring-2 ring-accent-default/40',
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
        className="!h-3 !w-3 !border-2 !border-[#0F0E0D] !bg-accent-default opacity-0 transition-opacity group-hover:opacity-100"
      />

      <div className="flex items-start gap-3">
        <div
          className={cn(
            'mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-border-base bg-[#121110] shadow-inner',
            languageTextClass(nodeData.language)
          )}
        >
          <Icon className="h-4 w-4" aria-hidden />
        </div>

        <div className="min-w-0 flex-1">
          <p className="truncate text-[13px] font-semibold tracking-tight text-text-primary transition-colors group-hover:text-accent-default">
            {nodeData.label}
          </p>
          <p className="mt-0.5 truncate text-[10px] text-text-tertiary">
            {nodeData.path.replace(/\\/g, '/').split('/').slice(-2).join('/')}
          </p>

          <div className="mt-2.5 flex items-center gap-2">
            <span
              className="rounded-md border px-2 py-0.5 text-[10px] font-medium"
              style={{
                color: accent,
                borderColor: `${accent}55`,
                backgroundColor: `${accent}18`,
              }}
            >
              {nodeData.language}
            </span>

            <div className="ml-auto flex items-center gap-1.5 text-[10px] font-semibold tabular-nums text-text-tertiary">
              <span className="flex items-center gap-0.5" title="Dependencies">
                <span className="text-accent-default">↓</span>
                {nodeData.dependencyCount}
              </span>
              <span className="text-border-base">·</span>
              <span className="flex items-center gap-0.5" title="Dependents">
                <span className="text-info">↑</span>
                {nodeData.dependentCount}
              </span>
            </div>
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

export const DependencyNode = memo(DependencyNodeComponent);
