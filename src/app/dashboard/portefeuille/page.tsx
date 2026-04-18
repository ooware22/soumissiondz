"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";
import type { CabinetEntreprise } from "@/lib/types";
import { Briefcase, Building2, ExternalLink } from "lucide-react";

export default function PortefeuillePage() {
  const { user } = useAuth();
  const [entreprises, setEntreprises] = useState<CabinetEntreprise[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.organisation_type !== "CABINET") {
      setLoading(false);
      return;
    }
    apiGet<CabinetEntreprise[]>("/cabinet/entreprises").then(setEntreprises).finally(() => setLoading(false));
  }, [user]);

  if (user?.organisation_type !== "CABINET") {
    return <div className="text-center py-12 text-muted-foreground">Cette page est réservée aux cabinets de consulting.</div>;
  }

  if (loading) return <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="skeleton h-20 w-full" />)}</div>;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2"><Briefcase className="h-6 w-6 text-indigo-400" />Portefeuille Clients</h1>
          <p className="mt-1 text-sm text-muted">Gérez les entreprises de votre portefeuille et suivez leurs dossiers.</p>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {entreprises.map(e => (
          <div key={e.id} className="rounded-xl border border-border bg-card p-5 hover:border-accent/50 transition-colors group cursor-pointer">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-surface flex items-center justify-center text-muted-foreground"><Building2 className="h-5 w-5" /></div>
                <div><h3 className="font-semibold group-hover:text-accent transition-colors">{e.nom}</h3><p className="text-xs text-muted-foreground">NIF: {e.nif || "-"}</p></div>
              </div>
              <ExternalLink className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            
            <div className="mt-5 grid grid-cols-3 gap-2 text-center divide-x divide-border">
              <div><p className="text-xs text-muted-foreground">AO</p><p className="font-bold">{e.nb_ao_actifs}</p></div>
              <div><p className="text-xs text-muted-foreground">Docs</p><p className="font-bold">{e.nb_documents}</p></div>
              <div><p className="text-xs text-muted-foreground">Score</p><p className={cn("font-bold", e.score_dernier_audit && e.score_dernier_audit >= 70 ? "text-success" : "text-warning")}>{e.score_dernier_audit || "-"}</p></div>
            </div>
            
            {e.nb_alertes > 0 && (
              <div className="mt-4 rounded-md bg-danger-muted px-3 py-2 text-xs text-danger font-medium text-center">
                {e.nb_alertes} alerte{e.nb_alertes > 1 ? "s" : ""} documentaire{e.nb_alertes > 1 ? "s" : ""}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
