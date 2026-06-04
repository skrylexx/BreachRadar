/**
 * lib/api.ts — Centralized BreachRadar HTTP Client
 * All API requests go through this layer.
 *
 * Features:
 *   - Fetch wrapper with HttpOnly cookie management
 *   - Redirect 401 → /login
 *   - Redirect 403 password expired
 *   - Domain-typed functions
 */

// ─── Base URL ──────────────────────────────────────────────────────────────────
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ─── Global Types ─────────────────────────────────────────────────────────────

export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "NONE";

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// ─── Fetch wrapper ─────────────────────────────────────────────────────────────

interface FetchOptions extends RequestInit {
  skipAuth?: boolean;
  suppressRedirect?: boolean;
}

export async function apiFetch<T = unknown>(
  path: string,
  options: FetchOptions = {}
): Promise<T> {
  const { skipAuth = false, suppressRedirect = false, ...fetchOptions } = options;

  const headers = new Headers(fetchOptions.headers ?? {});

  if (!headers.has("Content-Type") && fetchOptions.body) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...fetchOptions,
    headers,
    credentials: "include", // HttpOnly cookies (JWT)
  });

  // 401 → redirect to login
  if (response.status === 401 && !skipAuth && !suppressRedirect) {
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new Error("Unauthorized");
  }

  // 403 → password expired or insufficient permissions
  if (response.status === 403) {
    const data = await response.json().catch(() => ({}));
    if (response.headers.get("X-Password-Expired") === "true") {
      if (typeof window !== "undefined") {
        window.location.href = "/reset-password?expired=true";
      }
    }
    throw new Error(data.detail ?? "Forbidden");
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(errorData.detail ?? `HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

// ─── HTTP Helpers ──────────────────────────────────────────────────────────────
export const api = {
  get: <T>(path: string, options?: FetchOptions) =>
    apiFetch<T>(path, { ...options, method: "GET" }),

  post: <T>(path: string, body?: unknown, options?: FetchOptions) =>
    apiFetch<T>(path, {
      ...options,
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    }),

  patch: <T>(path: string, body?: unknown, options?: FetchOptions) =>
    apiFetch<T>(path, {
      ...options,
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    }),

  put: <T>(path: string, body?: unknown, options?: FetchOptions) =>
    apiFetch<T>(path, {
      ...options,
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(path: string, options?: FetchOptions) =>
    apiFetch<T>(path, { ...options, method: "DELETE" }),
};

// ─── Domain Types ──────────────────────────────────────────────────────────────

// Dashboard
export interface DashboardStats {
  scans_7d: number;
  critical_count: number;
  total_findings: number;
  last_scan_at: string | null;
}

export interface DashboardChartPoint {
  date: string;
  critical: number;
  high: number;
  medium: number;
  low: number;
}

// Scans
export interface Scan {
  id: string;
  started_at: string;
  finished_at: string | null;
  status: "running" | "completed" | "failed";
  duration_seconds: number | null;
  findings_count: number;
  severity: Severity;
  triggered_by: "cron" | "manual";
}

// Findings
export interface Finding {
  id: string;
  scan_id: string;
  source: string;
  type: string;
  severity: Severity;
  title: string;
  description: string;
  domain: string; // Add this
  discovered_at: string;
  metadata: Record<string, unknown>;
}

// Sources / Connectors
export interface ConnectorStatus {
  name: string;
  is_active: boolean;
  configured: boolean;
  is_mock?: boolean; // Add this
  status: "ok" | "warning" | "error" | "unknown" | "mock";
  last_scan_at: string | null;
  error_message?: string;
}

// Reports
export interface Report {
  id: string;
  generated_at: string;
  domain: string;
  severity: Severity;
  emails_compromised: number;
  has_ransomware_alert: boolean;
  type: "scheduled" | "manual";
  finding_counts: Record<Severity, number>;
}

// Ransomware alerts
export interface RansomwareAlert {
  id: string;
  group: string;
  victim: string;
  country?: string;
  sector?: string;
  claim_size?: string;
  status: "LISTED" | "PUBLISHED";
  discovered_at: string;
  published_at?: string;
  scan_id?: string;
}

// CVE
export interface CVEAlert {
  id: string;
  cve_id: string;
  title: string;
  description: string;
  severity: Severity;
  cvss_score: number | null;
  category: string;
  source: "NVD" | "OSV" | "GitHub" | "CVEFeed" | "custom";
  published_at: string;
}

export interface CVESettings {
  active_categories: string[];
  nvd_api_key?: string;
  polling_interval_minutes: number;
  include_no_cvss: boolean;
}

export interface CVESourceStatus {
  source: string;
  status: "ok" | "error" | "unknown";
  last_synced_at: string | null;
  item_count: number;
}

// Users (Admin)
export interface User {
  id: string;
  email: string;
  role: "admin" | "viewer";
  mfa_enabled: boolean;
  mfa_required: boolean;
  last_login_at: string | null;
  password_expires_at: string | null;
  is_active: boolean;
}

// API Keys (Admin)
export interface ApiKeyStatus {
  source: string;
  is_set: boolean;
  updated_at: string | null;
}

// Audit log
export interface AuditLogEntry {
  id: string;
  timestamp: string;
  user_email: string;
  action: string;
  ip_address: string;
  details?: Record<string, unknown>;
}

// ─── Fonctions typées par domaine ──────────────────────────────────────────────

// Dashboard
export const dashboardApi = {
  getStats: () => api.get<DashboardStats>("/api/v1/dashboard/stats"),
  getChart: (period = "7d") =>
    api.get<DashboardChartPoint[]>(`/api/v1/dashboard/chart?period=${period}`),
};

// Scans
export const scansApi = {
  list: (params?: { limit?: number; offset?: number }) => {
    const qs = new URLSearchParams({
      limit: String(params?.limit ?? 25),
      offset: String(params?.offset ?? 0),
    });
    return api.get<PaginatedResponse<Scan>>(`/api/v1/scans?${qs}`);
  },
  get: (id: string) => api.get<Scan>(`/api/v1/scans/${id}`),
  trigger: () => api.post<{ scan_id: string }>("/api/v1/scans/trigger"),
};

// Findings
export const findingsApi = {
  list: (params?: {
    limit?: number;
    offset?: number;
    source?: string;
    severity?: Severity;
    period?: string;
  }) => {
    const qs = new URLSearchParams();
    if (params?.limit) qs.set("limit", String(params.limit));
    if (params?.offset) qs.set("offset", String(params.offset));
    if (params?.source) qs.set("source", params.source);
    if (params?.severity) qs.set("severity", params.severity);
    if (params?.period) qs.set("period", params.period);
    return api.get<PaginatedResponse<Finding>>(`/api/v1/findings?${qs}`);
  },
};

// Sources / Connectors
export const sourcesApi = {
  getStatus: () => api.get<ConnectorStatus[]>("/api/v1/connectors/status"),
};

// Reports
export const reportsApi = {
  list: (params?: {
    limit?: number;
    offset?: number;
    period?: string;
    severity?: Severity;
  }) => {
    const qs = new URLSearchParams();
    if (params?.limit) qs.set("limit", String(params.limit));
    if (params?.offset) qs.set("offset", String(params.offset));
    if (params?.period) qs.set("period", params.period ?? "");
    if (params?.severity) qs.set("severity", params.severity);
    return api.get<PaginatedResponse<Report>>(`/api/v1/reports?${qs}`);
  },
  exportPdf: (id: string) => `${API_BASE}/api/v1/reports/${id}/export?format=pdf`,
  generate: (start: string, end: string) =>
    api.post<{ report_id: string }>("/api/v1/reports/generate", {
      start_date: start,
      end_date: end,
    }),
};

// Ransomware alerts
export const ransomwareApi = {
  getStatus: () => api.get<Record<string, unknown>>("/api/v1/ransomlook/status"),
  getAlerts: (params?: {
    limit?: number;
    offset?: number;
    group?: string;
    status?: string;
    period?: string;
  }) => {
    const qs = new URLSearchParams();
    if (params?.limit) qs.set("limit", String(params.limit));
    if (params?.offset) qs.set("offset", String(params.offset));
    if (params?.group) qs.set("group", params.group);
    if (params?.status) qs.set("status", params.status);
    if (params?.period) qs.set("period", params.period);
    return api.get<PaginatedResponse<RansomwareAlert>>(`/api/v1/ransomlook/alerts?${qs}`);
  },
};

// CVE
export const cveApi = {
  getAlerts: (params?: {
    limit?: number;
    offset?: number;
    severity?: Severity;
    category?: string;
    period?: string;
  }) => {
    const qs = new URLSearchParams();
    if (params?.limit) qs.set("limit", String(params.limit));
    if (params?.offset) qs.set("offset", String(params.offset));
    if (params?.severity) qs.set("severity", params.severity);
    if (params?.category) qs.set("category", params.category);
    if (params?.period) qs.set("period", params.period ?? "");
    return api.get<PaginatedResponse<CVEAlert>>(`/api/v1/cve/alerts?${qs}`);
  },
  getTrend: (period = "7d") =>
    api.get<DashboardChartPoint[]>(`/api/v1/cve/trend?period=${period}`),
  getStatus: () => api.get<CVESourceStatus[]>("/api/v1/cve/status"),
  getSettings: () => api.get<CVESettings>("/api/v1/cve/settings"),
  updateSettings: (settings: CVESettings) =>
    api.put<void>("/api/v1/cve/settings", settings),
};

// Users (Admin)
export const usersApi = {
  list: () => api.get<User[]>("/api/v1/users"),
  create: (data: { email: string; password: string; role: string }) =>
    api.post<User>("/api/v1/users", data),
  disable: (id: string) => api.patch<void>(`/api/v1/users/${id}/disable`),
  resetPassword: (id: string) =>
    api.post<void>(`/api/v1/users/${id}/reset-password`),
  resetMfa: (id: string) => api.post<void>(`/api/v1/users/${id}/reset-mfa`),
  requireMfa: (id: string) => api.post<void>(`/api/v1/users/${id}/require-mfa`),
};

// API Keys (Admin)
export const apiKeysApi = {
  list: () => api.get<ApiKeyStatus[]>("/api/v1/settings/api-keys"),
  set: (source: string, value: string) =>
    api.put<void>(`/api/v1/settings/api-keys/${source}`, { value }),
  delete: (source: string) =>
    api.delete<void>(`/api/v1/settings/api-keys/${source}`),
  test: (source: string) =>
    api.post<{ ok: boolean; message: string }>(
      `/api/v1/settings/api-keys/${source}/test`
    ),
};

// Audit log (Admin)
export const auditApi = {
  list: (params?: {
    limit?: number;
    offset?: number;
    user?: string;
    action?: string;
    period?: string;
  }) => {
    const qs = new URLSearchParams();
    if (params?.limit) qs.set("limit", String(params.limit));
    if (params?.offset) qs.set("offset", String(params.offset));
    if (params?.user) qs.set("user", params.user);
    if (params?.action) qs.set("action", params.action);
    if (params?.period) qs.set("period", params.period ?? "");
    return api.get<PaginatedResponse<AuditLogEntry>>(`/api/v1/audit?${qs}`);
  },
};

// Intelligence
export const intelligenceApi = {
  list: (params?: {
    page?: number;
    page_size?: number;
    finding_type?: string;
    severity?: Severity;
    source?: string;
    is_read?: boolean;
  }) => {
    const qs = new URLSearchParams();
    if (params?.page) qs.set("page", String(params.page));
    if (params?.page_size) qs.set("page_size", String(params.page_size));
    if (params?.finding_type) qs.set("finding_type", params.finding_type);
    if (params?.severity) qs.set("severity", params.severity);
    if (params?.source) qs.set("source", params.source);
    if (params?.is_read !== undefined) qs.set("is_read", String(params.is_read));
    return api.get<PaginatedResponse<any>>(`/api/v1/intelligence?${qs}`);
  },
  markAsRead: (id: string) => api.post<void>(`/api/v1/intelligence/${id}/read`),
  markAllAsRead: () => api.post<void>("/api/v1/intelligence/read-all"),
};

// Auth
export const authApi = {
  login: (email: string, password: string) =>
    api.post<{ requires_mfa: boolean; challenge_token?: string }>(
      "/api/v1/auth/login",
      { email, password },
      { skipAuth: true }
    ),
  mfaVerify: (challenge_token: string, totp_code: string) =>
    api.post<void>("/api/v1/auth/mfa/verify", { challenge_token, totp_code }, { skipAuth: true }),
  logout: () => api.post<void>("/api/v1/auth/logout"),
  me: () => api.get<User>("/api/v1/auth/me"),
  passwordChange: (data: any) =>
    api.post<User>("/api/v1/auth/password/change", data, { suppressRedirect: true }),
  mfaSetup: () =>
    api.post<{ qrcode_base64: string; manual_entry_key: string; backup_codes: string[] }>("/api/v1/auth/mfa/setup"),
  mfaConfirm: (code: string) =>
    api.post<User>("/api/v1/auth/mfa/confirm", { totp_code: code }, { suppressRedirect: true }),
  mfaDisable: (code: string) =>
    api.post<User>("/api/v1/auth/mfa/disable", { totp_code: code }, { suppressRedirect: true }),
};
