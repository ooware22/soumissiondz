"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDA, cn } from "@/lib/utils";
import type { AdminStats, AdminUser } from "@/lib/types";
import { ShieldAlert, Activity, Users, Building, FileText, Banknote } from "lucide-react";

export default function AdminPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role !== "ADMIN_PLATEFORME") {
      setLoading(false);
      return;
    }
    Promise.all([
      apiGet<AdminStats>("/admin/stats").catch(() => null),
      apiGet<AdminUser[]>("/admin/users").catch(() => []),
    ]).then(([s, u]) => { setStats(s); setUsers(u); setLoading(false); });
  }, [user]);

  if (user?.role !== "ADMIN_PLATEFORME") {
    return <div className="text-center py-12 text-muted-foreground">Accès refusé. Réservé aux administrateurs.</div>;
  }

  if (loading) return <div className="space-y-4">{[1,2,3].map(i => <div key={i} className="skeleton h-24 w-full" />)}</div>;

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2"><ShieldAlert className="h-6 w-6 text-red-500" />Administration</h1>
        <p className="mt-1 text-sm text-muted">Supervision globale de la plateforme Soumission DZ.</p>
      </div>

      {stats && (
        <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
          <div className="rounded-xl border border-border bg-card p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-2"><Building className="h-4 w-4" />Entreprises</div>
            <p className="text-2xl font-bold">{stats.total_entreprises}</p>
          </div>
          <div className="rounded-xl border border-border bg-card p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-2"><Users className="h-4 w-4" />Utilisateurs</div>
            <p className="text-2xl font-bold">{stats.total_users}</p>
          </div>
          <div className="rounded-xl border border-border bg-card p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-2"><FileText className="h-4 w-4" />Appels d&apos;offres</div>
            <p className="text-2xl font-bold">{stats.total_ao}</p>
          </div>
          <div className="rounded-xl border border-accent/50 bg-accent-muted/10 p-4">
            <div className="flex items-center gap-2 text-accent mb-2"><Banknote className="h-4 w-4" />Revenus (Mois)</div>
            <p className="text-2xl font-bold text-accent">{formatDA(stats.revenus_mois_da)}</p>
          </div>
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Activity className="h-5 w-5" />Utilisateurs Récents</h2>
        <div className="rounded-xl border border-border bg-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
            <thead><tr className="border-b border-border text-left">
              {["User", "Organisation", "Type", "Plan", "Statut"].map(h => <th key={h} className="px-5 py-3 text-xs font-medium uppercase text-muted-foreground">{h}</th>)}
            </tr></thead>
            <tbody>{users.map(u => (
              <tr key={u.id} className="border-b border-border/50 last:border-0 hover:bg-card-hover transition-colors">
                <td className="px-5 py-3"><p className="font-medium">{u.username}</p><p className="text-xs text-muted-foreground">{u.email}</p></td>
                <td className="px-5 py-3 font-medium">{u.organisation_nom}</td>
                <td className="px-5 py-3"><span className="text-xs rounded bg-surface px-2 py-0.5 border border-border">{u.organisation_type}</span></td>
                <td className="px-5 py-3 font-medium text-accent">{u.plan_code}</td>
                <td className="px-5 py-3">
                  <span className={cn("h-2 w-2 rounded-full inline-block mr-2", u.actif ? "bg-success" : "bg-danger")} />
                  {u.actif ? "Actif" : "Suspendu"}
                </td>
              </tr>
            ))}</tbody>
          </table>
          </div>
        </div>
      </div>
    </div>
  );
}
