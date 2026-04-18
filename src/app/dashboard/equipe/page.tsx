"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import { formatDateShort, cn } from "@/lib/utils";
import type { TeamMember } from "@/lib/types";
import { Users, UserPlus } from "lucide-react";

export default function EquipePage() {
  const [team, setTeam] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<TeamMember[]>("/team").then(setTeam).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="space-y-3">{[1,2].map(i => <div key={i} className="skeleton h-16 w-full" />)}</div>;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2"><Users className="h-6 w-6 text-blue-400" />Équipe & Accès</h1>
          <p className="mt-1 text-sm text-muted">Gérez les membres de votre organisation et leurs permissions.</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-surface border border-border px-4 py-2.5 text-sm font-medium text-foreground transition-all hover:border-border-hover">
          <UserPlus className="h-4 w-4" />Inviter
        </button>
      </div>

      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
            <table className="w-full text-sm">
          <thead><tr className="border-b border-border text-left">
            {["Utilisateur", "Rôle", "Statut", "Rejoint le", ""].map(h => <th key={h} className="px-5 py-3 text-xs font-medium uppercase text-muted-foreground">{h}</th>)}
          </tr></thead>
          <tbody>{team.map(m => (
            <tr key={m.id} className="border-b border-border/50 last:border-0 hover:bg-card-hover transition-colors">
              <td className="px-5 py-3">
                <p className="font-medium">{m.username}</p>
                <p className="text-xs text-muted-foreground">{m.email}</p>
              </td>
              <td className="px-5 py-3"><span className="rounded-md bg-accent/10 px-2 py-1 text-xs font-medium text-accent">{m.role}</span></td>
              <td className="px-5 py-3">
                <span className={cn("inline-flex items-center gap-1.5", m.actif ? "text-success" : "text-muted-foreground")}>
                  <span className={cn("h-2 w-2 rounded-full", m.actif ? "bg-success" : "bg-muted-foreground")} />
                  {m.actif ? "Actif" : "Désactivé"}
                </span>
              </td>
              <td className="px-5 py-3 text-muted">{formatDateShort(m.created_at)}</td>
              <td className="px-5 py-3 text-right">
                <button className="text-xs text-muted hover:text-foreground">Modifier</button>
              </td>
            </tr>
          ))}</tbody>
        </table>
          </div>
      </div>
    </div>
  );
}
