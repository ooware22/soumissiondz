"use client";

import { useEffect, useState, useCallback } from "react";
import { apiGet, apiPost, apiDelete } from "@/lib/api";
import { formatDA } from "@/lib/utils";
import type { Reference } from "@/lib/types";
import { BookOpen, Plus, X, Trash2, Loader2 } from "lucide-react";

export default function ReferencesPage() {
  const [refs, setRefs] = useState<Reference[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ objet: "", maitre_ouvrage: "", annee: "", montant_da: "", type_travaux: "" });

  const set = (k: string, v: string) => setForm(p => ({ ...p, [k]: v }));

  const load = useCallback(async () => {
    const data = await apiGet<Reference[]>("/references").catch(() => []);
    setRefs(data);
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload: Record<string, unknown> = { objet: form.objet };
      if (form.maitre_ouvrage) payload.maitre_ouvrage = form.maitre_ouvrage;
      if (form.annee) payload.annee = parseInt(form.annee);
      if (form.montant_da) payload.montant_da = parseInt(form.montant_da);
      if (form.type_travaux) payload.type_travaux = form.type_travaux;
      await apiPost("/references", payload);
      setShowForm(false);
      setForm({ objet: "", maitre_ouvrage: "", annee: "", montant_da: "", type_travaux: "" });
      await load();
    } catch { /* handled */ }
    setSaving(false);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Supprimer cette référence ?")) return;
    await apiDelete(`/references/${id}`);
    await load();
  };

  const inputCls = "w-full rounded-lg border border-border bg-input px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50";

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-purple-400" />
            Références de marchés
          </h1>
          <p className="mt-1 text-sm text-muted">Vos marchés exécutés, utilisés dans le mémoire technique.</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-accent-hover active:scale-[0.98]">
          {showForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showForm ? "Annuler" : "Ajouter"}
        </button>
      </div>

      {showForm && (
        <div className="rounded-xl border border-accent-border bg-accent-muted/30 p-5 animate-fade-in-scale">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-muted">Objet du marché *</label>
              <input value={form.objet} onChange={e => set("objet", e.target.value)} required minLength={3} placeholder="Réalisation d'un bâtiment R+4 - Blida" className={inputCls} />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Maître d&apos;ouvrage</label>
                <input value={form.maitre_ouvrage} onChange={e => set("maitre_ouvrage", e.target.value)} placeholder="DTP Wilaya de Blida" className={inputCls} />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Année</label>
                <input type="number" value={form.annee} onChange={e => set("annee", e.target.value)} min={1990} max={2100} placeholder="2024" className={inputCls} />
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Montant (DA)</label>
                <input type="number" value={form.montant_da} onChange={e => set("montant_da", e.target.value)} min={0} placeholder="45 000 000" className={inputCls} />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Type de travaux</label>
                <input value={form.type_travaux} onChange={e => set("type_travaux", e.target.value)} placeholder="Bâtiment, VRD, Routes..." className={inputCls} />
              </div>
            </div>
            <button type="submit" disabled={saving} className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-accent-hover disabled:opacity-50">
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
              Ajouter la référence
            </button>
          </form>
        </div>
      )}

      {loading ? (
        <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="skeleton h-14 w-full" />)}</div>
      ) : refs.length === 0 ? (
        <div className="rounded-xl border border-border bg-card p-12 text-center">
          <BookOpen className="mx-auto h-10 w-10 text-muted-foreground/40 mb-3" />
          <p className="text-sm text-muted">Aucune référence. Ajoutez vos marchés exécutés.</p>
        </div>
      ) : (
        <div className="rounded-xl border border-border bg-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                {["Objet", "Maître d'ouvrage", "Année", "Montant", "Type", ""].map(h => (
                  <th key={h} className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {refs.map(r => (
                <tr key={r.id} className="border-b border-border/50 last:border-0 hover:bg-card-hover transition-colors">
                  <td className="px-5 py-3 font-medium max-w-[250px] truncate">{r.objet}</td>
                  <td className="px-5 py-3 text-muted">{r.maitre_ouvrage || "-"}</td>
                  <td className="px-5 py-3 text-muted">{r.annee || "-"}</td>
                  <td className="px-5 py-3 text-muted">{r.montant_da ? formatDA(r.montant_da) : "-"}</td>
                  <td className="px-5 py-3"><span className="rounded-md bg-purple-500/10 px-2 py-0.5 text-xs font-medium text-purple-400">{r.type_travaux || "-"}</span></td>
                  <td className="px-5 py-3 text-right">
                    <button onClick={() => handleDelete(r.id)} className="rounded-md p-1.5 text-muted-foreground hover:text-danger hover:bg-danger-muted transition-colors">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        </div>
      )}
    </div>
  );
}
