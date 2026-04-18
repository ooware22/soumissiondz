"use client";

import { useEffect, useState, useCallback } from "react";
import { apiGet, apiPost, apiUpload } from "@/lib/api";
import { formatDA, formatDateShort, cn } from "@/lib/utils";
import type { AppelOffres, AuditResult } from "@/lib/types";
import { FileText, Plus, X, Upload, Search, Loader2, CheckCircle2, AlertTriangle, XCircle } from "lucide-react";

export default function AOPage() {
  const [aos, setAos] = useState<AppelOffres[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [saving, setSaving] = useState(false);
  const [importing, setImporting] = useState(false);
  const [audit, setAudit] = useState<{ aoId: number; data: AuditResult } | null>(null);
  const [auditing, setAuditing] = useState<number | null>(null);

  const [form, setForm] = useState({ reference: "", objet: "", maitre_ouvrage: "", wilaya_code: "", date_limite: "", budget_estime_da: "", qualification_requise_cat: "" });
  const set = (k: string, v: string) => setForm(p => ({ ...p, [k]: v }));

  const load = useCallback(async () => {
    const data = await apiGet<AppelOffres[]>("/ao").catch(() => []);
    setAos(data);
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload: Record<string, unknown> = { objet: form.objet };
      if (form.reference) payload.reference = form.reference;
      if (form.maitre_ouvrage) payload.maitre_ouvrage = form.maitre_ouvrage;
      if (form.wilaya_code) payload.wilaya_code = form.wilaya_code;
      if (form.date_limite) payload.date_limite = form.date_limite;
      if (form.budget_estime_da) payload.budget_estime_da = parseInt(form.budget_estime_da);
      if (form.qualification_requise_cat) payload.qualification_requise_cat = form.qualification_requise_cat;
      await apiPost("/ao", payload);
      setShowCreate(false);
      setForm({ reference: "", objet: "", maitre_ouvrage: "", wilaya_code: "", date_limite: "", budget_estime_da: "", qualification_requise_cat: "" });
      await load();
    } catch { /* handled */ }
    setSaving(false);
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImporting(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      await apiUpload("/ao/import-pdf", fd);
      await load();
    } catch { /* handled */ }
    setImporting(false);
    e.target.value = "";
  };

  const handleAudit = async (id: number) => {
    setAuditing(id);
    try {
      const data = await apiGet<AuditResult>(`/ao/${id}/audit`);
      setAudit({ aoId: id, data });
    } catch { /* handled */ }
    setAuditing(null);
  };

  const inputCls = "w-full rounded-lg border border-border bg-input px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50";

  const verdictIcon = (v: string) => {
    if (v === "ok") return <CheckCircle2 className="h-4 w-4 text-success shrink-0" />;
    if (v === "warning") return <AlertTriangle className="h-4 w-4 text-warning shrink-0" />;
    return <XCircle className="h-4 w-4 text-danger shrink-0" />;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
            <FileText className="h-6 w-6 text-sky-400" />
            Appels d&apos;offres
          </h1>
          <p className="mt-1 text-sm text-muted">Importez, créez et auditez vos AO.</p>
        </div>
        <div className="flex items-center gap-2">
          <label className={cn("flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2.5 text-sm font-medium text-muted cursor-pointer transition-all hover:text-foreground hover:border-border-hover", importing && "opacity-50")}>
            {importing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
            Importer PDF
            <input type="file" accept=".pdf" onChange={handleImport} className="hidden" disabled={importing} />
          </label>
          <button onClick={() => setShowCreate(!showCreate)} className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-accent-hover active:scale-[0.98]">
            {showCreate ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
            {showCreate ? "Annuler" : "Créer"}
          </button>
        </div>
      </div>

      {/* Create form */}
      {showCreate && (
        <div className="rounded-xl border border-accent-border bg-accent-muted/30 p-5 animate-fade-in-scale">
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Référence</label>
                <input value={form.reference} onChange={e => set("reference", e.target.value)} placeholder="AO-2026-042" className={inputCls} />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Objet *</label>
                <input value={form.objet} onChange={e => set("objet", e.target.value)} required minLength={3} placeholder="Réalisation d'un complexe sportif" className={inputCls} />
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Maître d&apos;ouvrage</label>
                <input value={form.maitre_ouvrage} onChange={e => set("maitre_ouvrage", e.target.value)} placeholder="DTP Blida" className={inputCls} />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Wilaya</label>
                <input value={form.wilaya_code} onChange={e => set("wilaya_code", e.target.value)} maxLength={3} placeholder="09" className={inputCls} />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Date limite</label>
                <input type="date" value={form.date_limite} onChange={e => set("date_limite", e.target.value)} className={inputCls} />
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Budget estimé (DA)</label>
                <input type="number" value={form.budget_estime_da} onChange={e => set("budget_estime_da", e.target.value)} min={0} placeholder="50 000 000" className={inputCls} />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Qualification</label>
                <input value={form.qualification_requise_cat} onChange={e => set("qualification_requise_cat", e.target.value)} maxLength={10} placeholder="Cat. III" className={inputCls} />
              </div>
            </div>
            <button type="submit" disabled={saving} className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-accent-hover disabled:opacity-50">
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
              Créer l&apos;AO
            </button>
          </form>
        </div>
      )}

      {/* AO list */}
      {loading ? (
        <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="skeleton h-14 w-full" />)}</div>
      ) : aos.length === 0 ? (
        <div className="rounded-xl border border-border bg-card p-12 text-center">
          <FileText className="mx-auto h-10 w-10 text-muted-foreground/40 mb-3" />
          <p className="text-sm text-muted">Aucun appel d&apos;offres. Importez un PDF ou créez-en un.</p>
        </div>
      ) : (
        <div className="rounded-xl border border-border bg-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                {["Réf.", "Objet", "MO", "Wilaya", "Limite", "Budget", ""].map(h => (
                  <th key={h} className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {aos.map(ao => (
                <tr key={ao.id} className="border-b border-border/50 last:border-0 hover:bg-card-hover transition-colors">
                  <td className="px-5 py-3 font-mono text-xs text-accent">{ao.reference || "-"}</td>
                  <td className="px-5 py-3 font-medium max-w-[200px] truncate">{ao.objet}</td>
                  <td className="px-5 py-3 text-muted max-w-[150px] truncate">{ao.maitre_ouvrage || "-"}</td>
                  <td className="px-5 py-3 text-muted">{ao.wilaya_code || "-"}</td>
                  <td className="px-5 py-3 text-muted">{ao.date_limite ? formatDateShort(ao.date_limite) : "-"}</td>
                  <td className="px-5 py-3 text-muted">{ao.budget_estime_da ? formatDA(ao.budget_estime_da) : "-"}</td>
                  <td className="px-5 py-3">
                    <button onClick={() => handleAudit(ao.id)} disabled={auditing === ao.id} className="flex items-center gap-1.5 rounded-md bg-accent-muted px-2.5 py-1 text-xs font-medium text-accent hover:bg-accent/20 transition-colors disabled:opacity-50">
                      {auditing === ao.id ? <Loader2 className="h-3 w-3 animate-spin" /> : <Search className="h-3 w-3" />}
                      Auditer
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        </div>
      )}

      {/* Audit result */}
      {audit && (
        <div className="rounded-xl border border-border bg-card p-6 animate-fade-in-scale">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold">Résultat d&apos;audit</h2>
              <p className="text-sm text-muted">25 règles analysées</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-6 text-sm">
                <span className="flex items-center gap-1"><CheckCircle2 className="h-4 w-4 text-success" /><b className="text-success">{audit.data.total_ok}</b></span>
                <span className="flex items-center gap-1"><AlertTriangle className="h-4 w-4 text-warning" /><b className="text-warning">{audit.data.total_warning}</b></span>
                <span className="flex items-center gap-1"><XCircle className="h-4 w-4 text-danger" /><b className="text-danger">{audit.data.total_danger}</b></span>
              </div>
              <div className={cn("flex h-16 w-16 items-center justify-center rounded-full text-xl font-bold",
                audit.data.score >= 70 ? "bg-success-muted text-success" : audit.data.score >= 40 ? "bg-warning-muted text-warning" : "bg-danger-muted text-danger"
              )}>
                {audit.data.score}
              </div>
            </div>
          </div>
          <div className="space-y-1">
            {audit.data.regles.map((r, i) => (
              <div key={i} className="flex items-start gap-3 rounded-lg px-3 py-2.5 hover:bg-card-hover transition-colors">
                {verdictIcon(r.verdict)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">{r.libelle}</span>
                    <span className="rounded-full bg-card px-1.5 py-0.5 text-[10px] text-muted-foreground">{r.categorie}</span>
                    <span className="text-[10px] text-muted-foreground">×{r.poids}</span>
                  </div>
                  <p className="text-xs text-muted mt-0.5">{r.message}</p>
                  {r.action && <p className="text-xs text-warning mt-0.5">→ {r.action}</p>}
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-border flex justify-end">
            <button onClick={() => setAudit(null)} className="text-sm text-muted hover:text-foreground transition-colors">Fermer</button>
          </div>
        </div>
      )}
    </div>
  );
}
