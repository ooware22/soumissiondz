"use client";
// ============================================================
// Soumission DZ - Login page
// Premium minimalistic design
// ============================================================

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { api } from "@/lib/api";
import { setToken } from "@/lib/api";
import Link from "next/link";
import {
  Zap,
  ArrowRight,
  Eye,
  EyeOff,
  AlertCircle,
  Loader2,
} from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { refresh } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await api<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: { email, password },
      });
      setToken(res.access_token);
      await refresh();
      router.push("/dashboard");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Identifiants invalides"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center px-4">
      {/* Background ambient glow */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-[20%] -top-[20%] h-[60%] w-[60%] rounded-full bg-accent/[0.04] blur-[120px]" />
        <div className="absolute -bottom-[20%] -right-[20%] h-[50%] w-[50%] rounded-full bg-purple-500/[0.03] blur-[120px]" />
      </div>

      <div className="relative w-full max-w-[400px] animate-fade-in">
        {/* Logo */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10 border border-accent-border">
            <Zap className="h-6 w-6 text-accent" />
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Soumission DZ
          </h1>
          <p className="mt-1 text-sm text-muted">
            Connectez-vous à votre espace
          </p>
        </div>

        {/* Form card */}
        <div className="rounded-2xl border border-border bg-card p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div>
              <label
                htmlFor="login-email"
                className="mb-1.5 block text-sm font-medium text-muted"
              >
                Email
              </label>
              <input
                id="login-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                placeholder="vous@entreprise.dz"
                className="w-full rounded-lg border border-border bg-input px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50"
              />
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="login-password"
                className="mb-1.5 block text-sm font-medium text-muted"
              >
                Mot de passe
              </label>
              <div className="relative">
                <input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  placeholder="••••••••"
                  className="w-full rounded-lg border border-border bg-input px-3 py-2.5 pr-10 text-sm text-foreground placeholder:text-muted-foreground transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="flex items-center gap-2 rounded-lg bg-danger-muted px-3 py-2.5 text-sm text-danger animate-fade-in-scale">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-accent-hover disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  Se connecter
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>
        </div>

        {/* Links */}
        <div className="mt-6 space-y-3 text-center text-sm">
          <p className="text-muted">
            Pas encore de compte ?{" "}
            <Link
              href="/signup/entreprise"
              className="text-accent hover:text-accent-hover transition-colors"
            >
              Créer une entreprise
            </Link>
            {" ou "}
            <Link
              href="/signup/cabinet"
              className="text-accent hover:text-accent-hover transition-colors"
            >
              un cabinet
            </Link>
          </p>
        </div>

        {/* Demo hint */}
        <div className="mt-8 rounded-xl border border-border bg-card/50 p-4">
          <p className="text-xs text-muted-foreground text-center">
            Démo :{" "}
            <button
              type="button"
              onClick={() => {
                setEmail("brahim@alpha-btph.dz");
                setPassword("Demo12345");
              }}
              className="text-accent hover:text-accent-hover transition-colors font-medium"
            >
              brahim@alpha-btph.dz
            </button>{" "}
            / Demo12345
          </p>
        </div>
      </div>
    </div>
  );
}
