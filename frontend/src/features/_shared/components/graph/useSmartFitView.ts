import { useCallback, useEffect, useRef } from 'react';
import { useReactFlow, useStore } from '@xyflow/react';
import { smartFitView } from '@/lib/graph-camera';

/**
 * Wait until ELK layout is ready and React Flow has painted nodes,
 * then animate an adaptive fit (~75–85% of viewport).
 */
export function useSmartFitView(layoutReady: boolean, nodeCount: number, layoutKey: string) {
  const { fitView, setViewport, getViewport, getNodes } = useReactFlow();
  const nodeCountInStore = useStore((s) => s.nodes.length);
  const fittedKeyRef = useRef<string | null>(null);

  const runFit = useCallback(() => {
    if (!layoutReady || nodeCount === 0 || nodeCountInStore === 0) return;
    const key = `${layoutKey}:${nodeCount}:${nodeCountInStore}`;
    if (fittedKeyRef.current === key) return;
    fittedKeyRef.current = key;

    // Double rAF + short delay so nodes finish measuring before camera moves.
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        window.setTimeout(() => {
          void smartFitView(
            fitView,
            { nodeCount, nodes: getNodes() },
            setViewport,
            getViewport
          );
        }, 120);
      });
    });
  }, [fitView, getNodes, getViewport, layoutReady, layoutKey, nodeCount, nodeCountInStore, setViewport]);

  useEffect(() => {
    runFit();
  }, [runFit]);

  return {
    refit: () => {
      fittedKeyRef.current = null;
      runFit();
    },
  };
}
