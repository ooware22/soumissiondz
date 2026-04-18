"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import { formatDA, formatDateShort, cn } from "@/lib/utils";
import type { Plan, Abonnement, Facture } from "@/lib/types";
import { CreditCard, CheckCircle2, Zap, Receipt } from "lucide-react";

export default function FacturationPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [abos, setAbos] = useState<Abonnement[]>([]);
  const [factures, setFactures] = useState<Facture[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiGet<Plan[]>("/plans").catch(() => []),
      apiGet<Abonnement[]>("/abonnements").catch(() => []),
      apiGet<Facture[]>("/factures").catch(() => []),
    ]).then(([p, a, f]) => { setPlans(p); setAbos(a); setFactures(f); setLoading(false); });
  }, []);

  if (loading) return <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="skeleton h-20 w-full" />)}</div>;

  const currentAbo = abos[0];

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
          <CreditCard className="h-6 w-6 text-emerald-400" />Facturation
        </h1>
        <p className="mt-1 text-sm text-muted">Gérez votre abonnement et consultez vos factures.</p>
      </div>

      {/* Current plan */}
      {currentAbo && (
        <div className="rounded-xl border border-accent/30 bg-accent-muted/20 p-6 glow-accent">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <p className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Abonnement actuel</p>
              <p className="text-xl font-bold flex items-center gap-2">
                <Zap className="h-5 w-5 text-accent" />
                Plan {currentAbo.plan_code}
              </p>
              <p className="mt-1 text-sm text-muted">{currentAbo.periodicite} - depuis le {formatDateShort(currentAbo.debut)}</p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-accent">{formatDA(currentAbo.montant_da)}</p>
              <p className="text-xs text-muted-foreground">/{currentAbo.periodicite === "mensuel" ? "mois" : "an"}</p>
            </div>
          </div>
        </div>
      )}

      {/* Plans grid */}
      <div>
        <h2 className="text-sm font-semibold mb-3">Plans disponibles</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {plans.filter(p => p.code !== "DECOUVERTE").map(p => {
            const isCurrent = currentAbo?.plan_code === p.code;
            return (
              <div key={p.code} className={cn("rounded-xl border p-5 transition-all hover:border-border-hover",
                isCurrent ? "border-accent/30 bg-accent-muted/20" : "border-border bg-card"
              )}>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold">{p.nom}</h3>
                  {isCurrent && <span className="rounded-full bg-accent/20 px-2 py-0.5 text-xs font-medium text-accent">Actuel</span>}
                </div>
                <p className="text-2xl font-bold">{formatDA(p.prix_mensuel_da)}<span className="text-sm text-muted-foreground font-normal">/mois</span></p>
                <p className="text-xs text-muted-foreground mt-1">ou {formatDA(p.prix_annuel_da)}/an (-10%)</p>
                {!isCurrent && (
                  <button className="mt-4 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm font-medium text-muted hover:text-foreground hover:border-border-hover transition-colors">
                    Changer de plan
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Invoices */}
      {factures.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <Receipt className="h-4 w-4 text-muted-foreground" />Factures
          </h2>
          <div className="rounded-xl border border-border bg-card overflow-hidden">
            <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-border text-left">
                {["N°", "Date", "Libellé", "HT", "TTC", "Statut"].map(h => (
                  <th key={h} className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">{h}</th>
                ))}
              </tr></thead>
              <tbody>{factures.map(f => (
                <tr key={f.id} className="border-b border-border/50 last:border-0 hover:bg-card-hover transition-colors">
                  <td className="px-5 py-3 font-mono text-xs text-accent">{f.numero}</td>
                  <td className="px-5 py-3 text-muted">{formatDateShort(f.date_emission)}</td>
                  <td className="px-5 py-3 font-medium">{f.libelle}</td>
                  <td className="px-5 py-3 text-muted">{formatDA(f.prix_ht_da)}</td>
                  <td className="px-5 py-3 font-medium">{formatDA(f.prix_ttc_da)}</td>
                  <td className="px-5 py-3">
                    <span className={cn("inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium",
                      f.statut === "payee" ? "bg-success-muted text-success" : "bg-warning-muted text-warning"
                    )}>
                      {f.statut === "payee" && <CheckCircle2 className="h-3 w-3" />}
                      {f.statut === "payee" ? "Payée" : "En attente"}
                    </span>
                  </td>
                </tr>
              ))}</tbody>
            </table>
          </div>
          </div>
        </div>
      )}
    </div>
  );
}
