// ============================================================
// Soumission DZ - API client
// Wraps fetch() with JWT auth and error handling
// When USE_MOCK=true, all calls go through mock-api.ts
// ============================================================

import { USE_MOCK, mockApi } from "@/lib/mock-api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";
const TOKEN_KEY = "sdz_token";
const ME_KEY = "sdz_me";

// ---------- Token management ----------

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearSession(): void {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(ME_KEY);
}

export function getStoredMe(): unknown {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(ME_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setStoredMe(me: unknown): void {
  sessionStorage.setItem(ME_KEY, JSON.stringify(me));
}

// ---------- API error ----------

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
    this.name = "ApiError";
  }
}

// ---------- Fetch wrapper ----------

interface FetchOptions extends Omit<RequestInit, "body"> {
  body?: unknown | FormData;
}

export async function api<T = unknown>(
  path: string,
  opts: FetchOptions = {}
): Promise<T> {
  // Mock mode: bypass fetch entirely
  if (USE_MOCK) {
    return mockApi<T>(path, { method: (opts.method as string) || "GET", body: opts.body });
  }

  const headers: Record<string, string> = {};
  const token = getToken();

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let body: BodyInit | undefined;

  if (opts.body instanceof FormData) {
    body = opts.body;
  } else if (opts.body !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(opts.body);
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...opts,
    headers: { ...headers, ...(opts.headers as Record<string, string>) },
    body,
  });

  if (res.status === 401) {
    clearSession();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new ApiError(401, "Session expirée");
  }

  const text = await res.text();
  let data: T;
  try {
    data = text ? JSON.parse(text) : (null as T);
  } catch {
    data = text as unknown as T;
  }

  if (!res.ok) {
    const detail =
      (data as { detail?: string })?.detail ||
      `Erreur HTTP ${res.status}`;
    throw new ApiError(
      res.status,
      typeof detail === "string" ? detail : JSON.stringify(detail)
    );
  }

  return data;
}

// ---------- Convenience methods ----------

export const apiGet = <T = unknown>(path: string) =>
  api<T>(path);

export const apiPost = <T = unknown>(path: string, body?: unknown) =>
  api<T>(path, { method: "POST", body });

export const apiPatch = <T = unknown>(path: string, body?: unknown) =>
  api<T>(path, { method: "PATCH", body });

export const apiDelete = <T = unknown>(path: string) =>
  api<T>(path, { method: "DELETE" });

export const apiUpload = <T = unknown>(path: string, formData: FormData) =>
  api<T>(path, { method: "POST", body: formData });
