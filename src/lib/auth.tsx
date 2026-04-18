"use client";
// ============================================================
// Soumission DZ - Auth context provider
// ============================================================

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import type { MeResponse, LoginRequest } from "@/lib/types";
import {
  api,
  getToken,
  setToken,
  clearSession,
  getStoredMe,
  setStoredMe,
} from "@/lib/api";
import { mockSetUser } from "@/lib/mock-api";

interface AuthContextType {
  user: MeResponse | null;
  loading: boolean;
  login: (creds: LoginRequest) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const me = await api<MeResponse>("/auth/me");
      setUser(me);
      setStoredMe(me);
    } catch {
      setUser(null);
      clearSession();
    }
  }, []);

  useEffect(() => {
    const token = getToken();
    if (token) {
      const stored = getStoredMe() as MeResponse | null;
      if (stored) {
        setUser(stored);
        mockSetUser(stored); // sync mock state
      }
      refresh().finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [refresh]);

  const login = useCallback(
    async (creds: LoginRequest) => {
      const res = await api<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: creds,
      });
      setToken(res.access_token);
      await refresh();
    },
    [refresh]
  );

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
    window.location.href = "/login";
  }, []);

  return (
    <AuthContext value={{ user, loading, login, logout, refresh }}>
      {children}
    </AuthContext>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
