import { memo } from 'react';
import {
  BaseEdge,
  getSmoothStepPath,
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
  style,
}: EdgeProps) {
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

  const weight = typeof data?.weight === 'number' ? data.weight : 1;
  const dimmed = Boolean(data?.dimmed);
  const emphasized = Boolean(data?.emphasized) || selected;
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

export const DependencyEdge = memo(DependencyEdgeComponent);
