import type { Run, RunSummary, Source, Passage, Audit, CreateRunRequest } from '../types/api';

const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true';
const BASE_URL  = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(status: number, body: unknown) {
    super(`API error ${status}`);
    this.status = status;
    this.body = body;
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body);
  }
  return res.json() as Promise<T>;
}

export async function createRun(
  req: CreateRunRequest,
): Promise<{ run_id: string; stream_url: string }> {
  if (USE_MOCKS) {
    return { run_id: 'mock-run-001', stream_url: '/api/runs/mock-run-001/events' };
  }
  return apiFetch('/api/runs', { method: 'POST', body: JSON.stringify(req) });
}

export async function getRun(id: string): Promise<Run> {
  if (USE_MOCKS) {
    const { mockRun } = await import('../mocks/mockData');
    return mockRun;
  }
  return apiFetch(`/api/runs/${id}`);
}

export async function listRuns(): Promise<RunSummary[]> {
  if (USE_MOCKS) {
    const { mockRunSummaries } = await import('../mocks/mockData');
    return mockRunSummaries;
  }
  return apiFetch('/api/runs');
}

export async function getSources(id: string): Promise<Source[]> {
  if (USE_MOCKS) {
    const { mockSources } = await import('../mocks/mockData');
    return mockSources;
  }
  return apiFetch<{ sources: Source[] }>(`/api/runs/${id}/sources`).then(r => r.sources);
}

export async function getEvidence(id: string): Promise<Passage[]> {
  if (USE_MOCKS) {
    const { mockPassages } = await import('../mocks/mockData');
    return mockPassages;
  }
  return apiFetch<{ passages: Passage[] }>(`/api/runs/${id}/evidence`).then(r => r.passages);
}

export async function getAudit(id: string): Promise<Audit> {
  if (USE_MOCKS) {
    const { mockAudit } = await import('../mocks/mockData');
    return mockAudit;
  }
  return apiFetch(`/api/runs/${id}/audit`);
}

export async function downloadExport(
  id: string,
  format: 'md' | 'html' | 'json',
): Promise<Blob> {
  const res = await fetch(`${BASE_URL}/api/runs/${id}/export/${format}`);
  if (!res.ok) throw new ApiError(res.status, {});
  return res.blob();
}
