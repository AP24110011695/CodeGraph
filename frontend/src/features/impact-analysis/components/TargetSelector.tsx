import type { UseMutationResult } from '@tanstack/react-query';
import { Button } from '@/design-system/primitives/Button';
import { useNotificationStore } from '@/core/store/notification.store';
import { isAPIError } from '@/core/api/errors';
import type { ImpactAnalyzeRequest, ImpactAnalyzeResponse } from '../api/impact.types';
import { useImpactStore } from '../store/impact.store';

interface TargetSelectorProps {
  analyzeMutation: UseMutationResult<
    ImpactAnalyzeResponse,
    unknown,
    ImpactAnalyzeRequest
  >;
  onAnalyzed?: (result: ImpactAnalyzeResponse) => void;
}

const TARGET_TYPES = ['auto', 'class', 'module', 'file', 'api', 'symbol'] as const;
const CHANGE_TYPES = ['modify', 'delete', 'rename', 'add'] as const;

export function TargetSelector({ analyzeMutation, onAnalyzed }: TargetSelectorProps) {
  const target = useImpactStore((s) => s.target);
  const targetType = useImpactStore((s) => s.targetType);
  const changeType = useImpactStore((s) => s.changeType);
  const setTarget = useImpactStore((s) => s.setTarget);
  const setTargetType = useImpactStore((s) => s.setTargetType);
  const setChangeType = useImpactStore((s) => s.setChangeType);
  const addNotification = useNotificationStore((s) => s.addNotification);

  const onAnalyze = async () => {
    if (!target.trim()) {
      addNotification({
        title: 'Target required',
        description: 'Enter a class, module, file, or API symbol to analyze.',
        tone: 'warning',
      });
      return;
    }

    try {
      const response = await analyzeMutation.mutateAsync({
        target: target.trim(),
        target_type: targetType,
        change_type: changeType,
      });
      addNotification({
        title: 'Impact analysis complete',
        description: `Analyzed change to "${target.trim()}"`,
        tone: 'success',
      });
      onAnalyzed?.(response);
    } catch (error) {
      addNotification({
        title: 'Impact analysis failed',
        description: isAPIError(error) ? error.message : 'Unknown error',
        tone: 'danger',
      });
    }
  };

  return (
    <div className="rounded-md border border-border-base bg-bg-elevated p-4">
      <h3 className="mb-3 text-sm font-medium text-text-primary">Change target</h3>
      <div className="grid gap-3 md:grid-cols-[1fr_auto_auto_auto]">
        <input
          type="text"
          value={target}
          onChange={(event) => setTarget(event.target.value)}
          placeholder="Class, module, file, or API symbol"
          className="h-9 rounded-md border border-border-base bg-bg-base px-3 text-sm text-text-primary"
          aria-label="Impact target"
        />
        <select
          value={targetType}
          onChange={(event) => setTargetType(event.target.value)}
          className="h-9 rounded-md border border-border-base bg-bg-base px-2 text-xs text-text-primary"
          aria-label="Target type"
        >
          {TARGET_TYPES.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
        <select
          value={changeType}
          onChange={(event) => setChangeType(event.target.value)}
          className="h-9 rounded-md border border-border-base bg-bg-base px-2 text-xs text-text-primary"
          aria-label="Change type"
        >
          {CHANGE_TYPES.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
        <Button
          variant="primary"
          size="sm"
          disabled={analyzeMutation.isPending}
          onClick={() => void onAnalyze()}
        >
          {analyzeMutation.isPending ? 'Analyzing…' : 'Analyze impact'}
        </Button>
      </div>
    </div>
  );
}
