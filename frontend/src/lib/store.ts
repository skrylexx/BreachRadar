"use client";

import { create } from 'zustand';

// ─── Sidebar open/close ───────────────────────────────────────────────────────

interface SidebarState {
  isOpen: boolean;
  open: () => void;
  close: () => void;
  toggle: () => void;
}

export const useSidebarStore = create<SidebarState>((set) => ({
  isOpen: false,
  open: () => set({ isOpen: true }),
  close: () => set({ isOpen: false }),
  toggle: () => set((state) => ({ isOpen: !state.isOpen })),
}));

// ─── API Keys configured status cache ────────────────────────────────────────
// Stores a lightweight dict { service_name → configured } loaded once on mount.
// Used by the Sidebar to split nav items between connected/disconnected tools.

interface ApiKeyStatusState {
  /** Map of service_name → configured (boolean). Null = not yet loaded. */
  configuredStatus: Record<string, boolean> | null;
  /** True while fetching the status from the API. */
  loading: boolean;
  /** Set the map after successful fetch. */
  setConfiguredStatus: (status: Record<string, boolean>) => void;
  /** Mark loading state. */
  setLoading: (loading: boolean) => void;
  /** Returns true if the given service has an active API key configured. */
  isConfigured: (serviceName: string) => boolean;
}

export const useApiKeyStatusStore = create<ApiKeyStatusState>((set, get) => ({
  configuredStatus: null,
  loading: false,
  setConfiguredStatus: (status) => set({ configuredStatus: status, loading: false }),
  setLoading: (loading) => set({ loading }),
  isConfigured: (serviceName) => {
    const map = get().configuredStatus;
    if (!map) return false;
    return map[serviceName] === true;
  },
}));
