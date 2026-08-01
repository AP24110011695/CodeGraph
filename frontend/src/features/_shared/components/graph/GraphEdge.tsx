import { memo } from 'react';
import {
  BaseEdge,
  getSmoothStepPath,
  type EdgeProps,
} from '@xyflow/react';

export type GraphEdgeData = {
  weight?: number;
  relation?: string;
  dimmed?: boolean;
  emphasized?: boolean;
};

function GraphEdgeComponent({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  selected,
  data,
  style,
}: EdgeProps) {
  const edgeData = (data ?? {}) as GraphEdgeData;
  const [path] = getSmoothStepPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    borderRadius: 16,
    offset: 12,
  });

  const weight = typeof edgeData.weight === 'number' ? edgeData.weight : 1;
  const dimmed = Boolean(edgeData.dimmed);
  const emphasized = Boolean(edgeData.emphasized) || selected;
  const baseWidth = Math.min(3, 1.1 + weight * 0.35);

  return (
    <>
      <BaseEdge
        id={id}
        path={path}
        style={{
          stroke: emphasized ? '#E8A045' : '#3A342E',
          strokeWidth: emphasized ? baseWidth + 0.8 : baseWidth,
          strokeOpacity: dimmed ? 0.08 : emphasized ? 1 : 0.45,
          transition: 'stroke 0.25s ease, stroke-opacity 0.25s ease, stroke-width 0.25s ease',
          ...style,
        }}
      />
      {emphasized && (
        <circle r="2.5" fill="#E8A045" opacity={0.9}>
          <animateMotion dur="1.6s" repeatCount="indefinite" path={path} />
        </circle>
      )}
    </>
  );
}

export const GraphEdge = memo(GraphEdgeComponent);
