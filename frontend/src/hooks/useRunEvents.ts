import { useEffect, useRef, useState, useCallback } from 'react';
import type { SSEEvent, StageId, StageStatus, Source } from '../types/api';

export interface StageState {
  id:     StageId;
  status: StageStatus;
}

export interface RunEventState {
  stages:    Record<StageId, StageStatus>;
  plan:      { scope: string; query_variants: string[] } | null;
  sources:   Source[];
  logs:      Array<{ stage: StageId; level: string; message: string; ts: string }>;
  complete:  boolean;
  error:     string | null;
  connected: boolean;
}

const initialStages: Record<StageId, StageStatus> = {
  scope:   'idle',
  plan:    'idle',
  search:  'idle',
  fetch:   'idle',
  extract: 'idle',
  rank:    'idle',
  write:   'idle',
  verify:  'idle',
};

export function useRunEvents(runId: string | null, enabled = true): RunEventState {
  const [state, setState] = useState<RunEventState>({
    stages:    { ...initialStages },
    plan:      null,
    sources:   [],
    logs:      [],
    complete:  false,
    error:     null,
    connected: false,
  });

  const retryCount = useRef(0);
  const esRef      = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (!runId || !enabled) return;

    const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const es       = new EventSource(`${BASE_URL}/api/runs/${runId}/events`);
    esRef.current  = es;

    es.onopen = () => {
      retryCount.current = 0;
      setState(s => ({ ...s, connected: true, error: null }));
    };

    es.onmessage = (e: MessageEvent) => {
      try {
        const ev = JSON.parse(e.data as string) as SSEEvent;

        setState(s => {
          switch (ev.event) {
            case 'stage':
              return { ...s, stages: { ...s.stages, [ev.stage]: ev.status } };

            case 'plan_ready':
              return { ...s, plan: ev.plan };

            case 'source':
              return { ...s, sources: [...s.sources, ev.source] };

            case 'source_update':
              return {
                ...s,
                sources: s.sources.map(src =>
                  src.source_id === ev.source_id
                    ? {
                        ...src,
                        status:            ev.status,
                        snippet:           ev.snippet           ?? src.snippet,
                        credibility_score: ev.credibility_score ?? src.credibility_score,
                      }
                    : src,
                ),
              };

            case 'log':
              return {
                ...s,
                logs: [
                  ...s.logs,
                  { stage: ev.stage, level: ev.level, message: ev.message, ts: ev.ts },
                ],
              };

            case 'complete':
              return { ...s, complete: true };

            case 'error':
              return { ...s, error: ev.message };

            default:
              return s;
          }
        });
      } catch {
        // Silently ignore malformed SSE frames
      }
    };

    es.onerror = () => {
      es.close();
      setState(s => ({ ...s, connected: false }));

      const delay = Math.min(1000 * Math.pow(2, retryCount.current), 8000);
      retryCount.current += 1;

      if (retryCount.current <= 3) {
        setTimeout(connect, delay);
      }
    };
  }, [runId, enabled]);

  useEffect(() => {
    connect();
    return () => {
      esRef.current?.close();
    };
  }, [connect]);

  return state;
}
