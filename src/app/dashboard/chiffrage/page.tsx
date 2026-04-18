"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";
import { formatDA, cn } from "@/lib/utils";
import type { PrixArticle, Template, SimulationResult } from "@/lib/types";
import { Calculator, Plus, X, Loader2, TrendingUp, TrendingDown, Minus, BarChart3 } from "lucide-react";

interface Poste { article_code: string; quantite: string; prix_propose_da: string; }

export default function ChiffragePage() {
  const [articles, setArticles] = useState<PrixArticle[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"simuler" | "template">("simuler");
  const [postes, setPostes] = useState<Poste[]>([{ article_code: "", quantite: "", prix_propose_da: "" }]);
  const [simResult, setSimResult] = useState<SimulationResult | null>(null);
  const [simulating, setSimulating] = useState(false);
  const [tplCode, setTplCode] = useState("");
  const [tplBudget, setTplBudget] = useState("");
  const [tplResult, setTplResult] = useState<unknown>(null);
  const [chiffrant, setChiffrant] = useState(false);

  useEffect(() => {
    Promise.all([
      apiGet<PrixArticle[]>("/prix/articles").catch(() => []),
      apiGet<Template[]>("/templates").catch(() => []),
    ]).then(([a, t]) => {
      setArticles(a); setTemplates(t);
      if (a.length) setPostes([{ article_code: a[0].code, quantite: "100", prix_propose_da: String(a[0].prix_moy_da) }]);
      if (t.length) setTplCode(t[0].code);
      setLoading(false);
    });
  }, []);

  const addPoste = () => setPostes([...postes, { article_code: articles[0]?.code || "", quantite: "", prix_propose_da: "" }]);
  const removePoste = (i: number) => setPostes(postes.filter((_, j) => j !== i));
  const updatePoste = (i: number, k: keyof Poste, v: string) => {
    const next = [...postes]; next[i] = { ...next[i], [k]: v }; setPostes(next);
  };

  const handleSimuler = async () => {
    setSimulating(true);
    try {
      const body = { postes: postes.filter(p => p.article_code && p.quantite).map(p => ({ article_code: p.article_code, quantite: Number(p.quantite), prix_propose_da: Number(p.prix_propose_da) })) };
      const res = await apiPost<SimulationResult>("/prix/simuler", body);
      setSimResult(res);
    } catch { /* */ }
    setSimulating(false);
  };

  const handleChiffrer = async () => {
    setChiffrant(true);
    try {
      const res = await apiPost(`/templates/${tplCode}/chiffrer`, { budget_cible_da: Number(tplBudget) });
      setTplResult(res);
    } catch { /* */ }
    setChiffrant(false);
  };

  const inputCls = "w-full rounded-lg border border-border bg-input px-3 py-2 text-sm text-foreground transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50";
  const verdictColor = (v: string) => v === "ok" ? "text-success" : v === "bas" || v === "haut" ? "text-warning" : "text-danger";
  const verdictIcon = (v: string) => v === "ok" ? <Minus className="h-3.5 w-3.5" /> : v === "haut" ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />;

  if (loading) return <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="skeleton h-14 w-full" />)}</div>;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2"><Calculator className="h-6 w-6 text-emerald-400" />Chiffrage & Prix</h1>
        <p className="mt-1 text-sm text-muted">Simulez vos prix et générez des DQE à partir de templates.</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg bg-surface p-1 border border-border w-fit">
        {(["simuler", "template"] as const).map(t => (
          <button key={t} onClick={() => setTab(t)} className={cn("rounded-md px-4 py-2 text-sm font-medium transition-colors", tab === t ? "bg-card text-foreground shadow-sm" : "text-muted hover:text-foreground")}>
            {t === "simuler" ? "Simuler prix" : "Template DQE"}
          </button>
        ))}
      </div>

      {tab === "simuler" && (
        <div className="space-y-4">
          <div className="rounded-xl border border-border bg-card p-5 space-y-3">
            {postes.map((p, i) => (
              <div key={i} className="flex gap-3 items-end">
                <div className="flex-1">
                  {i === 0 && <label className="mb-1 block text-xs text-muted-foreground">Article</label>}
                  <select value={p.article_code} onChange={e => updatePoste(i, "article_code", e.target.value)} className={inputCls}>
                    {articles.map(a => <option key={a.code} value={a.code}>{a.code} - {a.libelle}</option>)}
                  </select>
                </div>
                <div className="w-24">
                  {i === 0 && <label className="mb-1 block text-xs text-muted-foreground">Qté</label>}
                  <input type="number" value={p.quantite} onChange={e => updatePoste(i, "quantite", e.target.value)} placeholder="100" className={inputCls} />
                </div>
                <div className="w-32">
                  {i === 0 && <label className="mb-1 block text-xs text-muted-foreground">Prix proposé (DA)</label>}
                  <input type="number" value={p.prix_propose_da} onChange={e => updatePoste(i, "prix_propose_da", e.target.value)} placeholder="26000" className={inputCls} />
                </div>
                <button onClick={() => removePoste(i)} className="rounded-md p-2 text-muted-foreground hover:text-danger hover:bg-danger-muted transition-colors mb-0.5"><X className="h-4 w-4" /></button>
              </div>
            ))}
            <div className="flex gap-2 pt-2">
              <button onClick={addPoste} className="flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-xs text-muted hover:text-foreground hover:border-border-hover transition-colors"><Plus className="h-3.5 w-3.5" />Ajouter</button>
              <button onClick={handleSimuler} disabled={simulating} className="flex items-center gap-1.5 rounded-lg bg-accent px-4 py-2 text-xs font-medium text-white transition-all hover:bg-accent-hover disabled:opacity-50">
                {simulating ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <BarChart3 className="h-3.5 w-3.5" />}Simuler
              </button>
            </div>
          </div>

          {simResult && (
            <div className="rounded-xl border border-border bg-card p-5 animate-fade-in-scale space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">Résultat de simulation</h3>
                <div className={cn("rounded-full px-3 py-1 text-sm font-bold", simResult.ecart_global_pct > 10 ? "bg-danger-muted text-danger" : simResult.ecart_global_pct < -10 ? "bg-warning-muted text-warning" : "bg-success-muted text-success")}>
                  {simResult.ecart_global_pct > 0 ? "+" : ""}{simResult.ecart_global_pct}%
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div><span className="text-muted-foreground">Total proposé:</span> <b>{formatDA(simResult.montant_total_propose_da)}</b></div>
                <div><span className="text-muted-foreground">Total référence:</span> <b>{formatDA(simResult.montant_total_reference_da)}</b></div>
              </div>
              <div className="overflow-x-auto">
            <table className="w-full text-sm">
                <thead><tr className="border-b border-border text-left">
                  {["Article", "Qté", "Proposé", "Réf.", "Écart", ""].map(h => <th key={h} className="px-3 py-2 text-xs font-medium uppercase text-muted-foreground">{h}</th>)}
                </tr></thead>
                <tbody>{simResult.postes.map((p, i) => (
                  <tr key={i} className="border-b border-border/50 last:border-0">
                    <td className="px-3 py-2 font-medium">{p.libelle}</td>
                    <td className="px-3 py-2 text-muted">{p.quantite}</td>
                    <td className="px-3 py-2">{formatDA(p.prix_propose_da)}</td>
                    <td className="px-3 py-2 text-muted">{formatDA(p.prix_moy_da)}</td>
                    <td className={cn("px-3 py-2 font-medium", verdictColor(p.verdict))}>{p.ecart_vs_moy_pct > 0 ? "+" : ""}{p.ecart_vs_moy_pct}%</td>
                    <td className={cn("px-3 py-2", verdictColor(p.verdict))}>{verdictIcon(p.verdict)}</td>
                  </tr>
                ))}</tbody>
              </table>
          </div>
            </div>
          )}

          {/* Price reference table */}
          <div className="rounded-xl border border-border bg-card overflow-hidden">
            <div className="border-b border-border px-5 py-3"><h3 className="text-sm font-semibold">Référentiel de prix</h3></div>
            <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-border text-left">
                {["Code", "Libellé", "Catégorie", "Unité", "Min", "Moy", "Max"].map(h => <th key={h} className="px-4 py-2.5 text-xs font-medium uppercase text-muted-foreground">{h}</th>)}
              </tr></thead>
              <tbody>{articles.map(a => (
                <tr key={a.code} className="border-b border-border/50 last:border-0 hover:bg-card-hover transition-colors">
                  <td className="px-4 py-2.5 font-mono text-xs text-accent">{a.code}</td>
                  <td className="px-4 py-2.5 font-medium">{a.libelle}</td>
                  <td className="px-4 py-2.5"><span className="rounded-md bg-accent-muted px-2 py-0.5 text-xs text-accent">{a.categorie}</span></td>
                  <td className="px-4 py-2.5 text-muted">{a.unite}</td>
                  <td className="px-4 py-2.5 text-muted">{formatDA(a.prix_min_da)}</td>
                  <td className="px-4 py-2.5 font-medium">{formatDA(a.prix_moy_da)}</td>
                  <td className="px-4 py-2.5 text-muted">{formatDA(a.prix_max_da)}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
          </div>
        </div>
      )}

      {tab === "template" && (
        <div className="space-y-4">
          <div className="rounded-xl border border-border bg-card p-5 space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Template</label>
                <select value={tplCode} onChange={e => setTplCode(e.target.value)} className={inputCls}>
                  {templates.map(t => <option key={t.code} value={t.code}>{t.nom} ({formatDA(t.budget_reference_da)})</option>)}
                </select>
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Budget cible (DA)</label>
                <input type="number" value={tplBudget} onChange={e => setTplBudget(e.target.value)} placeholder="80000000" className={inputCls} />
              </div>
            </div>
            <button onClick={handleChiffrer} disabled={chiffrant || !tplBudget} className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-accent-hover disabled:opacity-50">
              {chiffrant ? <Loader2 className="h-4 w-4 animate-spin" /> : <Calculator className="h-4 w-4" />}Générer le DQE
            </button>
          </div>
          {tplResult && (
            <div className="rounded-xl border border-border bg-card p-5 animate-fade-in-scale">
              <h3 className="font-semibold mb-3">DQE généré</h3>
              <pre className="text-xs text-muted bg-surface rounded-lg p-4 overflow-auto max-h-[400px]">{JSON.stringify(tplResult, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
