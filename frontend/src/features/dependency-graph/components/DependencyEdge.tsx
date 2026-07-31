import { memo } from 'react';
import {
  BaseEdge,
  getBezierPath,
  type EdgeProps,
} from '@xyflow/react';

function DependencyEdgeComponent({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  selected,
  data,
}: EdgeProps) {
  const [path] = getBezierPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
  });

  const weight = typeof data?.weight === 'number' ? data.weight : 1;

  return (
    <BaseEdge
      id={id}
      path={path}
      style={{
        stroke: selected ? '#7C3AED' : '#2A2A2A',
        strokeWidth: Math.min(3, 1 + weight * 0.5),
      }}
    />
  );
}

export const DependencyEdge = memo(DependencyEdgeComponent);
