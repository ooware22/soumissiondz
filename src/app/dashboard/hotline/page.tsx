"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import { formatDateShort, cn } from "@/lib/utils";
import type { Ticket } from "@/lib/types";
import { LifeBuoy, Plus, MessageCircle, CheckCircle2 } from "lucide-react";

export default function HotlinePage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<Ticket[]>("/hotline").then(setTickets).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="space-y-3">{[1,2].map(i => <div key={i} className="skeleton h-24 w-full" />)}</div>;

  const prioriteColor = (p: string) => {
    if (p === "haute") return "text-danger bg-danger-muted";
    if (p === "moyenne") return "text-warning bg-warning-muted";
    return "text-muted bg-surface";
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2"><LifeBuoy className="h-6 w-6 text-rose-400" />Support & Hotline</h1>
          <p className="mt-1 text-sm text-muted">Contactez notre équipe d&apos;experts pour toute question technique ou métier.</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-accent-hover">
          <Plus className="h-4 w-4" />Nouveau ticket
        </button>
      </div>

      <div className="space-y-4">
        {tickets.length === 0 ? (
          <div className="rounded-xl border border-border bg-card p-12 text-center text-muted-foreground">
            <MessageCircle className="mx-auto h-12 w-12 opacity-20 mb-3" />
            <p>Aucun ticket ouvert.</p>
          </div>
        ) : (
          tickets.map(t => (
            <div key={t.id} className="rounded-xl border border-border bg-card p-5 hover:border-border-hover transition-colors">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-mono text-xs text-muted-foreground">#{t.id}</span>
                    <span className={cn("rounded px-2 py-0.5 text-[10px] font-bold uppercase", prioriteColor(t.priorite))}>{t.priorite}</span>
                    {t.statut === "resolu" && <span className="flex items-center gap-1 rounded text-[10px] font-bold uppercase text-success bg-success-muted px-2 py-0.5"><CheckCircle2 className="h-3 w-3" />Résolu</span>}
                  </div>
                  <h3 className="font-semibold text-lg">{t.sujet}</h3>
                  <p className="mt-2 text-sm text-muted leading-relaxed">{t.message}</p>
                </div>
                <div className="text-xs text-muted-foreground whitespace-nowrap">{formatDateShort(t.created_at)}</div>
              </div>
              
              {t.reponse && (
                <div className="mt-4 rounded-lg bg-accent-muted/20 border border-accent/20 p-4">
                  <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-accent"><LifeBuoy className="h-3.5 w-3.5" />Réponse de l&apos;équipe</div>
                  <p className="text-sm">{t.reponse}</p>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
