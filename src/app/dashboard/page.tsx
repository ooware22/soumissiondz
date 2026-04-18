"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { apiGet } from "@/lib/api";
import { formatDA, formatDateShort, cn } from "@/lib/utils";
import type { Document, AlerteExpiration, Reference, AppelOffres, Facture } from "@/lib/types";
import { FileText, AlertTriangle, BookOpen, ScrollText, Receipt, ArrowUpRight, Clock } from "lucide-react";

interface KpiData {
  docs: Document[];
  alertes: AlerteExpiration[];
  refs: Reference[];
  aos: AppelOffres[];
  factures: Facture[];
}

const KPI_CFG = [
  { key: "docs", label: "Documents", icon: FileText, color: "text-accent", bg: "bg-accent-muted" },
  { key: "alertes", label: "Alertes", icon: AlertTriangle, color: "", bg: "" },
  { key: "refs", label: "Références", icon: BookOpen, color: "text-purple-400", bg: "bg-purple-500/10" },
  { key: "aos", label: "AO actifs", icon: ScrollText, color: "text-sky-400", bg: "bg-sky-500/10" },
  { key: "factures", label: "Factures", icon: Receipt, color: "text-emerald-400", bg: "bg-emerald-500/10" },
] as const;

export default function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState<KpiData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiGet<Document[]>("/coffre/documents").catch(() => []),
      apiGet<AlerteExpiration[]>("/coffre/alertes").catch(() => []),
      apiGet<Reference[]>("/references").catch(() => []),
      apiGet<AppelOffres[]>("/ao").catch(() => []),
      apiGet<Facture[]>("/factures").catch(() => []),
    ]).then(([docs, alertes, refs, aos, factures]) => {
      setData({ docs, alertes, refs, aos, factures });
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Tableau de bord</h1>
        <p className="mt-1 text-sm text-muted">Bienvenue, {user?.username}. Voici un aperçu de votre activité.</p>
      </div>

      {/* KPIs */}
      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="rounded-xl border border-border bg-card p-5">
              <div className="skeleton h-4 w-20 mb-3" />
              <div className="skeleton h-8 w-12" />
            </div>
          ))}
        </div>
      ) : data && (
        <div className="stagger grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {KPI_CFG.map((cfg) => {
            const count = data[cfg.key].length;
            const color = cfg.key === "alertes" ? (count > 0 ? "text-danger" : "text-success") : cfg.color;
            const bg = cfg.key === "alertes" ? (count > 0 ? "bg-danger-muted" : "bg-success-muted") : cfg.bg;
            return (
              <div key={cfg.key} className="group relative overflow-hidden rounded-xl border border-border bg-card p-5 transition-all hover:border-border-hover hover:bg-card-hover">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{cfg.label}</span>
                  <div className={cn("rounded-lg p-1.5", bg)}><cfg.icon className={cn("h-3.5 w-3.5", color)} /></div>
                </div>
                <p className={cn("mt-3 text-3xl font-bold tracking-tight", color)}>{count}</p>
                <ArrowUpRight className="absolute bottom-3 right-3 h-4 w-4 text-muted-foreground/0 transition-all group-hover:text-muted-foreground/40" />
              </div>
            );
          })}
        </div>
      )}

      {/* Alerts table */}
      {data && data.alertes.length > 0 && (
        <div className="rounded-xl border border-border bg-card">
          <div className="flex items-center gap-2 border-b border-border px-5 py-4">
            <Clock className="h-4 w-4 text-warning" />
            <h2 className="text-sm font-semibold">Alertes d&apos;expiration</h2>
            <span className="ml-auto rounded-full bg-warning-muted px-2 py-0.5 text-xs font-medium text-warning">{data.alertes.length}</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                {["Document", "Expiration", "Reste", "Seuil"].map((h) => (
                  <th key={h} className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.alertes.map((a, i) => (
                <tr key={i} className="border-b border-border/50 last:border-0 hover:bg-card-hover transition-colors">
                  <td className="px-5 py-3 font-medium">{a.type_code}</td>
                  <td className="px-5 py-3 text-muted">{formatDateShort(a.date_expiration)}</td>
                  <td className="px-5 py-3">{a.jours_restants < 0 ? <span className="text-danger font-medium">Expiré</span> : `${a.jours_restants}j`}</td>
                  <td className="px-5 py-3">
                    <span className={cn("inline-flex rounded-full px-2 py-0.5 text-xs font-medium",
                      a.seuil === "expire" || a.seuil === "7j" ? "bg-danger-muted text-danger" : a.seuil === "15j" ? "bg-warning-muted text-warning" : "bg-accent-muted text-accent"
                    )}>{a.seuil}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        </div>
      )}

      {/* Recent AOs */}
      {data && data.aos.length > 0 && (
        <div className="rounded-xl border border-border bg-card">
          <div className="flex items-center gap-2 border-b border-border px-5 py-4">
            <ScrollText className="h-4 w-4 text-accent" />
            <h2 className="text-sm font-semibold">Appels d&apos;offres récents</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                {["Réf.", "Objet", "Wilaya", "Date limite", "Budget"].map((h) => (
                  <th key={h} className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.aos.slice(0, 5).map((ao) => (
                <tr key={ao.id} className="border-b border-border/50 last:border-0 hover:bg-card-hover transition-colors">
                  <td className="px-5 py-3 font-mono text-xs text-accent">{ao.reference || "-"}</td>
                  <td className="px-5 py-3 font-medium max-w-[300px] truncate">{ao.objet}</td>
                  <td className="px-5 py-3 text-muted">{ao.wilaya_code || "-"}</td>
                  <td className="px-5 py-3 text-muted">{ao.date_limite ? formatDateShort(ao.date_limite) : "-"}</td>
                  <td className="px-5 py-3 text-muted">{ao.budget_estime_da ? formatDA(ao.budget_estime_da) : "-"}</td>
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
