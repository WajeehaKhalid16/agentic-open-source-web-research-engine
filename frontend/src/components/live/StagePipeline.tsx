// ─── StagePipeline ────────────────────────────────────────────────────────────
// Renders the full ordered pipeline of stage nodes.

import { stages } from '../../tokens/tokens';
import type { StageId, StageStatus } from '../../types/api';
import { StageNode } from './StageNode';

interface Props {
  stageStates: Record<StageId, StageStatus>;
}

export function StagePipeline({ stageStates }: Props) {
  return (
    <div
      className="flex items-center justify-center flex-wrap gap-0"
      role="region"
      aria-label="Research progress"
      aria-live="polite"
    >
      {stages.map((s, i) => (
        <StageNode
          key={s.id}
          id={s.id as StageId}
          label={s.label}
          status={stageStates[s.id as StageId]}
          isLast={i === stages.length - 1}
        />
      ))}
    </div>
  );
}
