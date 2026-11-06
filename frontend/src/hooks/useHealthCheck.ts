import { useEffect, useState } from 'react';

export type HealthStatus = 'checking' | 'ok' | 'error';

export function useHealthCheck(): HealthStatus {
  const [status, setStatus] = useState<HealthStatus>('checking');
  const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch(`${BASE_URL}/health`, {
          signal: AbortSignal.timeout(3000),
        });
        setStatus(res.ok ? 'ok' : 'error');
      } catch {
        setStatus('error');
      }
    };

    check();
    const interval = setInterval(check, 30_000);
    return () => clearInterval(interval);
  }, [BASE_URL]);

  return status;
}
