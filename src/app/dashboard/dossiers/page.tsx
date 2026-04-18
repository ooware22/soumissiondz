"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { KanbanData, Dossier } from "@/lib/types";
import { Kanban, FileStack, ArrowRight, CheckCircle2 } from "lucide-react";

const COLUMNS: { key: keyof KanbanData; label: string; color: string; bg: string }[] = [
  { key: "a_faire", label: "À faire", color: "text-muted", bg: "bg-zinc-800" },
  { key: "en_cours", label: "En cours", color: "text-accent", bg: "bg-accent-muted" },
  { key: "a_valider", label: "À valider", color: "text-warning", bg: "bg-warning-muted" },
  { key: "termine", label: "Terminé", color: "text-success", bg: "bg-success-muted" },
];

const ETAPE_LABELS: Record<string, string> = {
  profil: "Profil", documents: "Documents", audit: "Audit",
  chiffrage: "Chiffrage", memoire: "Mémoire", verification: "Vérification", depot: "Dépôt",
};

function DossierCard({ d }: { d: Dossier }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-3.5 hover:border-border-hover transition-colors cursor-pointer group">
      <p className="text-sm font-medium group-hover:text-accent transition-colors">{d.nom}</p>
      <div className="mt-2 flex items-center justify-between">
        <span className="rounded-md bg-card px-2 py-0.5 text-[11px] text-muted-foreground">
          {ETAPE_LABELS[d.etape_actuelle] || d.etape_actuelle}
        </span>
        {d.score_audit !== undefined && (
          <span className={cn(
            "text-xs font-bold",
            d.score_audit >= 70 ? "text-success" : d.score_audit >= 40 ? "text-warning" : "text-danger"
          )}>
            {d.score_audit}/100
          </span>
        )}
      </div>
      {d.date_cible && <p className="mt-1.5 text-[11px] text-muted-foreground">Limite: {d.date_cible}</p>}
    </div>
  );
}

export default function DossiersPage() {
  const [data, setData] = useState<KanbanData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<KanbanData>("/dossiers/kanban")
      .then(setData)
      .catch(() => setData({ a_faire: [], en_cours: [], a_valider: [], termine: [] }))
      .finally(() => setLoading(false));
  }, []);

  const total = data ? Object.values(data).reduce((s, col) => s + col.length, 0) : 0;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
            <Kanban className="h-6 w-6 text-orange-400" />
            Dossiers de soumission
          </h1>
          <p className="mt-1 text-sm text-muted">
            {total} dossier{total !== 1 ? "s" : ""} en cours de traitement.
          </p>
        </div>
      </div>

      {/* Pipeline legend */}
      <div className="flex items-center gap-1 text-xs text-muted-foreground overflow-x-auto pb-1">
        {Object.keys(ETAPE_LABELS).map((e, i, arr) => (
          <span key={e} className="flex items-center gap-1 whitespace-nowrap">
            <span className="rounded bg-card px-1.5 py-0.5">{ETAPE_LABELS[e]}</span>
            {i < arr.length - 1 && <ArrowRight className="h-3 w-3" />}
          </span>
        ))}
        <CheckCircle2 className="h-3 w-3 text-success ml-1" />
      </div>

      {/* Kanban board */}
      {loading ? (
        <div className="grid grid-cols-4 gap-4">
          {[1,2,3,4].map(i => <div key={i} className="skeleton h-48 rounded-xl" />)}
        </div>
      ) : data && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {COLUMNS.map(col => (
            <div key={col.key} className="rounded-xl border border-border bg-card min-h-[200px]">
              <div className="flex items-center justify-between border-b border-border px-4 py-3">
                <span className={cn("text-sm font-semibold", col.color)}>{col.label}</span>
                <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", col.bg, col.color)}>
                  {data[col.key].length}
                </span>
              </div>
              <div className="p-3 space-y-2">
                {data[col.key].length === 0 ? (
                  <div className="flex items-center justify-center py-8">
                    <FileStack className="h-6 w-6 text-muted-foreground/30" />
                  </div>
                ) : (
                  data[col.key].map(d => <DossierCard key={d.id} d={d} />)
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
