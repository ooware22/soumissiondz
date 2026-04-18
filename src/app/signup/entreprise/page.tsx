"use client";
// ============================================================
// Soumission DZ - Signup Entreprise (Cas 1)
// ============================================================

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { api, setToken } from "@/lib/api";
import Link from "next/link";
import {
  Zap,
  ArrowRight,
  ArrowLeft,
  Building2,
  AlertCircle,
  Loader2,
} from "lucide-react";

export default function SignupEntreprisePage() {
  const router = useRouter();
  const { refresh } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    nom_entreprise: "",
    forme_juridique: "",
    email: "",
    username: "",
    password: "",
    telephone: "",
  });

  const set = (key: string, value: string) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const payload = { ...form };
      if (!payload.forme_juridique) delete (payload as Record<string, unknown>).forme_juridique;
      if (!payload.telephone) delete (payload as Record<string, unknown>).telephone;

      const res = await api<{ access_token: string }>("/signup/entreprise", {
        method: "POST",
        body: payload,
      });
      setToken(res.access_token);
      await refresh();
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de la création");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center px-4 py-12">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-[20%] -top-[20%] h-[60%] w-[60%] rounded-full bg-accent/[0.04] blur-[120px]" />
      </div>

      <div className="relative w-full max-w-[440px] animate-fade-in">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10 border border-accent-border">
            <Building2 className="h-6 w-6 text-accent" />
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Créer votre entreprise
          </h1>
          <p className="mt-1 text-sm text-muted">
            Cas 1 - Entreprise autonome
          </p>
        </div>

        {/* Form */}
        <div className="rounded-2xl border border-border bg-card p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="signup-nom" className="mb-1.5 block text-sm font-medium text-muted">
                Nom de l&apos;entreprise
              </label>
              <input
                id="signup-nom"
                value={form.nom_entreprise}
                onChange={(e) => set("nom_entreprise", e.target.value)}
                required
                minLength={2}
                placeholder="Alpha BTPH"
                className="w-full rounded-lg border border-border bg-input px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50"
              />
            </div>

            <div>
              <label htmlFor="signup-forme" className="mb-1.5 block text-sm font-medium text-muted">
                Forme juridique
              </label>
              <select
                id="signup-forme"
                value={form.forme_juridique}
                onChange={(e) => set("forme_juridique", e.target.value)}
                className="w-full rounded-lg border border-border bg-input px-3 py-2.5 text-sm text-foreground transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50"
              >
                <option value="">- Sélectionner -</option>
                <option value="SARL">SARL</option>
                <option value="SPA">SPA</option>
                <option value="EURL">EURL</option>
                <option value="SNC">SNC</option>
                <option value="ETI">ETI</option>
                <option value="AUTO-ENTREPRENEUR">Auto-entrepreneur</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="signup-email" className="mb-1.5 block text-sm font-medium text-muted">
                  Email
                </label>
                <input
                  id="signup-email"
                  type="email"
                  value={form.email}
                  onChange={(e) => set("email", e.target.value)}
                  required
                  placeholder="vous@entreprise.dz"
                  className="w-full rounded-lg border border-border bg-input px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50"
                />
              </div>
              <div>
                <label htmlFor="signup-username" className="mb-1.5 block text-sm font-medium text-muted">
                  Nom d&apos;utilisateur
                </label>
                <input
                  id="signup-username"
                  value={form.username}
                  onChange={(e) => set("username", e.target.value)}
                  required
                  minLength={2}
                  placeholder="brahim"
                  className="w-full rounded-lg border border-border bg-input px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="signup-password" className="mb-1.5 block text-sm font-medium text-muted">
                  Mot de passe (8+ car.)
                </label>
                <input
                  id="signup-password"
                  type="password"
                  value={form.password}
                  onChange={(e) => set("password", e.target.value)}
                  required
                  minLength={8}
                  placeholder="••••••••"
                  className="w-full rounded-lg border border-border bg-input px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50"
                />
              </div>
              <div>
                <label htmlFor="signup-tel" className="mb-1.5 block text-sm font-medium text-muted">
                  Téléphone
                </label>
                <input
                  id="signup-tel"
                  value={form.telephone}
                  onChange={(e) => set("telephone", e.target.value)}
                  placeholder="0555 XX XX XX"
                  className="w-full rounded-lg border border-border bg-input px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50"
                />
              </div>
            </div>

            {error && (
              <div className="flex items-center gap-2 rounded-lg bg-danger-muted px-3 py-2.5 text-sm text-danger animate-fade-in-scale">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-accent-hover disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  Créer mon compte
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>
        </div>

        <div className="mt-6 text-center">
          <Link
            href="/login"
            className="inline-flex items-center gap-1.5 text-sm text-muted hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Retour à la connexion
          </Link>
        </div>
      </div>
    </div>
  );
}
