const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export type UserSession = {
  id: number;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
};

export function getAuthToken() {
  return localStorage.getItem('token');
}

export function setAuthToken(token: string) {
  localStorage.setItem('token', token);
}

export function clearAuthToken() {
  localStorage.removeItem('token');
}

function getErrorMessage(data: unknown, fallback: string): string {
  if (!data || typeof data !== 'object') return fallback;

  const payload = data as { detail?: unknown; message?: unknown };
  if (typeof payload.detail === 'string') return payload.detail;
  if (Array.isArray(payload.detail)) {
    const messages = payload.detail
      .map((issue) => issue && typeof issue === 'object' && 'msg' in issue && typeof issue.msg === 'string' ? issue.msg : '')
      .filter(Boolean);
    if (messages.length) return messages.join('; ');
  }
  return typeof payload.message === 'string' ? payload.message : fallback;
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> | undefined),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(getErrorMessage(data, 'Request failed'));
  }
  return data as T;
}

export async function apiUpload(path: string, file: File) {
  const token = getAuthToken();
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    body: formData,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(getErrorMessage(data, 'Upload failed'));
  }
  return data;
}
