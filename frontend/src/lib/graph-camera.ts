import type { ReactFlowInstance, Node } from '@xyflow/react';
import { classifyGraphSize } from './elk-layout';

export interface AdaptiveFitOptions {
  nodeCount: number;
  duration?: number;
  /** Override padding (fraction of viewport). Lower = fills more of the view. */
  padding?: number;
  nodes?: Node[];
  widthHint?: number;
  heightHint?: number;
}

/**
 * Adaptive fitView: graph should occupy ~75–85% of the viewport.
 * Small repos zoom in more; large repos get a slightly wider padding.
 */
export function adaptiveFitOptions(nodeCount: number): {
  padding: number;
  maxZoom: number;
  minZoom: number;
  duration: number;
} {
  const band = classifyGraphSize(nodeCount);
  if (band === 'small') {
    return { padding: 0.16, maxZoom: 1.4, minZoom: 0.4, duration: 700 };
  }
  if (band === 'medium') {
    return { padding: 0.1, maxZoom: 1.15, minZoom: 0.35, duration: 800 };
  }
  return { padding: 0.08, maxZoom: 1.0, minZoom: 0.28, duration: 900 };
}

function boundsOf(nodes: Node[], widthHint = 240, heightHint = 96) {
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const node of nodes) {
    const w = node.measured?.width ?? widthHint;
    const h = node.measured?.height ?? heightHint;
    minX = Math.min(minX, node.position.x);
    minY = Math.min(minY, node.position.y);
    maxX = Math.max(maxX, node.position.x + w);
    maxY = Math.max(maxY, node.position.y + h);
  }
  if (!Number.isFinite(minX)) {
    return { minX: 0, minY: 0, maxX: 1, maxY: 1, width: 1, height: 1 };
  }
  return {
    minX,
    minY,
    maxX,
    maxY,
    width: Math.max(1, maxX - minX),
    height: Math.max(1, maxY - minY),
  };
}

/**
 * Prefer filling ~80% of viewport width when the graph is still tall,
 * so we never open on a tiny vertical strip.
 */
export async function smartFitView(
  fitView: ReactFlowInstance['fitView'],
  options: AdaptiveFitOptions,
  setViewport?: ReactFlowInstance['setViewport'],
  getViewport?: ReactFlowInstance['getViewport']
): Promise<void> {
  const tuned = adaptiveFitOptions(options.nodeCount);

  if (options.nodes && options.nodes.length > 0 && setViewport) {
    const bounds = boundsOf(options.nodes, options.widthHint, options.heightHint);
    const aspect = bounds.width / bounds.height;
    const isTall = aspect < 1.15;

    if (isTall) {
      // Width-first fit: fill ~82% of viewport width, clamp zoom.
      const pane = document.querySelector('.react-flow') as HTMLElement | null;
      const vw = pane?.clientWidth || window.innerWidth;
      const vh = pane?.clientHeight || window.innerHeight;
      const targetWidth = vw * 0.82;
      const zoomByWidth = targetWidth / bounds.width;
      const zoomByHeight = (vh * 0.88) / bounds.height;
      const zoom = Math.max(
        tuned.minZoom,
        Math.min(tuned.maxZoom, Math.min(zoomByWidth, Math.max(zoomByHeight, zoomByWidth * 0.9)))
      );
      const cx = bounds.minX + bounds.width / 2;
      const cy = bounds.minY + bounds.height / 2;
      const x = vw / 2 - cx * zoom;
      const y = vh / 2 - cy * zoom;
      setViewport({ x, y, zoom }, { duration: options.duration ?? tuned.duration });
      return;
    }

    // Wide / balanced graphs: occupy ~80–85% of the viewport.
    // When the graph is short/wide, prefer filling height without overflowing width.
    {
      const pane = document.querySelector('.react-flow') as HTMLElement | null;
      const vw = pane?.clientWidth || window.innerWidth;
      const vh = pane?.clientHeight || window.innerHeight;
      const zW = (vw * 0.84) / bounds.width;
      const zH = (vh * 0.84) / bounds.height;
      const zoom =
        aspect > 1.35
          ? Math.max(tuned.minZoom, Math.min(tuned.maxZoom, Math.min(zH, (vw * 0.92) / bounds.width)))
          : Math.max(tuned.minZoom, Math.min(tuned.maxZoom, Math.min(zW, zH)));
      const cx = bounds.minX + bounds.width / 2;
      const cy = bounds.minY + bounds.height / 2;
      setViewport(
        { x: vw / 2 - cx * zoom, y: vh / 2 - cy * zoom, zoom },
        { duration: options.duration ?? tuned.duration }
      );
      return;
    }
  }

  await fitView({
    padding: options.padding ?? tuned.padding,
    duration: options.duration ?? tuned.duration,
    maxZoom: tuned.maxZoom,
    minZoom: tuned.minZoom,
  });

  // Nudge: if still too small after fitView, bump zoom toward filling width.
  if (getViewport && setViewport && options.nodes && options.nodes.length > 0) {
    const vp = getViewport();
    const band = classifyGraphSize(options.nodeCount);
    const floor = band === 'small' ? 0.6 : band === 'medium' ? 0.42 : 0.32;
    if (vp.zoom < floor) {
      const pane = document.querySelector('.react-flow') as HTMLElement | null;
      const vw = pane?.clientWidth || window.innerWidth;
      const vh = pane?.clientHeight || window.innerHeight;
      const bounds = boundsOf(options.nodes, options.widthHint, options.heightHint);
      const zoom = Math.min(tuned.maxZoom, Math.max(floor, (vw * 0.8) / bounds.width));
      const cx = bounds.minX + bounds.width / 2;
      const cy = bounds.minY + bounds.height / 2;
      setViewport(
        { x: vw / 2 - cx * zoom, y: vh / 2 - cy * zoom, zoom },
        { duration: Math.round((options.duration ?? tuned.duration) * 0.6) }
      );
    }
  }
}

export function nodeCenter(position: { x: number; y: number }, width = 220, height = 90) {
  return {
    x: position.x + width / 2,
    y: position.y + height / 2,
  };
}
