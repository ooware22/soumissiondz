"use client";
// ============================================================
// Soumission DZ - Signup Cabinet (Cas 2)
// ============================================================

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { api, setToken } from "@/lib/api";
import Link from "next/link";
import {
  ArrowRight,
  ArrowLeft,
  Briefcase,
  AlertCircle,
  Loader2,
} from "lucide-react";

export default function SignupCabinetPage() {
  const router = useRouter();
  const { refresh } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    nom_cabinet: "",
    consultant_principal: "",
    email: "",
    username: "",
    password: "",
  });

  const set = (key: string, value: string) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await api<{ access_token: string }>("/signup/cabinet", {
        method: "POST",
        body: form,
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

  const inputCls =
    "w-full rounded-lg border border-border bg-input px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50";

  return (
    <div className="relative flex min-h-screen items-center justify-center px-4 py-12">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -right-[20%] -top-[20%] h-[60%] w-[60%] rounded-full bg-purple-500/[0.03] blur-[120px]" />
      </div>

      <div className="relative w-full max-w-[440px] animate-fade-in">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/10 border border-purple-500/20">
            <Briefcase className="h-6 w-6 text-purple-400" />
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Créer votre cabinet
          </h1>
          <p className="mt-1 text-sm text-muted">
            Cas 2 - Consultant multi-entreprises
          </p>
        </div>

        <div className="rounded-2xl border border-border bg-card p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="cab-nom" className="mb-1.5 block text-sm font-medium text-muted">
                Nom du cabinet
              </label>
              <input id="cab-nom" value={form.nom_cabinet} onChange={(e) => set("nom_cabinet", e.target.value)} required minLength={2} placeholder="Cabinet Mourad Conseils" className={inputCls} />
            </div>
            <div>
              <label htmlFor="cab-consul" className="mb-1.5 block text-sm font-medium text-muted">
                Consultant principal
              </label>
              <input id="cab-consul" value={form.consultant_principal} onChange={(e) => set("consultant_principal", e.target.value)} required minLength={2} placeholder="Mourad Benali" className={inputCls} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="cab-email" className="mb-1.5 block text-sm font-medium text-muted">Email</label>
                <input id="cab-email" type="email" value={form.email} onChange={(e) => set("email", e.target.value)} required placeholder="vous@cabinet.dz" className={inputCls} />
              </div>
              <div>
                <label htmlFor="cab-user" className="mb-1.5 block text-sm font-medium text-muted">Nom d&apos;utilisateur</label>
                <input id="cab-user" value={form.username} onChange={(e) => set("username", e.target.value)} required minLength={2} placeholder="mourad" className={inputCls} />
              </div>
            </div>
            <div>
              <label htmlFor="cab-pass" className="mb-1.5 block text-sm font-medium text-muted">Mot de passe (8+ car.)</label>
              <input id="cab-pass" type="password" value={form.password} onChange={(e) => set("password", e.target.value)} required minLength={8} placeholder="••••••••" className={inputCls} />
            </div>

            {error && (
              <div className="flex items-center gap-2 rounded-lg bg-danger-muted px-3 py-2.5 text-sm text-danger animate-fade-in-scale">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button type="submit" disabled={loading} className="flex w-full items-center justify-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-accent-hover disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <><span>Créer le cabinet</span><ArrowRight className="h-4 w-4" /></>}
            </button>
          </form>
        </div>

        <div className="mt-6 text-center">
          <Link href="/login" className="inline-flex items-center gap-1.5 text-sm text-muted hover:text-foreground transition-colors">
            <ArrowLeft className="h-3.5 w-3.5" />
            Retour à la connexion
          </Link>
        </div>
      </div>
    </div>
  );
}
