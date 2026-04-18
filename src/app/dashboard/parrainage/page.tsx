"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import { formatDA } from "@/lib/utils";
import type { Parrainage } from "@/lib/types";
import { Gift, Copy, Check, Share2 } from "lucide-react";

export default function ParrainagePage() {
  const [data, setData] = useState<Parrainage | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    apiGet<Parrainage>("/parrainage/mon-code").then(setData).finally(() => setLoading(false));
  }, []);

  const copyCode = () => {
    if (!data) return;
    navigator.clipboard.writeText(data.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) return <div className="skeleton h-64 w-full rounded-xl" />;
  if (!data) return null;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2"><Gift className="h-6 w-6 text-yellow-400" />Parrainage</h1>
        <p className="mt-1 text-sm text-muted">Invitez vos confrères et gagnez des commissions sur leurs abonnements.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-xl border border-accent/30 bg-accent-muted/10 p-6 glow-accent flex flex-col justify-center text-center">
          <h2 className="text-lg font-semibold mb-2">Votre code de parrainage</h2>
          <p className="text-sm text-muted mb-6">Partagez ce code. Chaque nouvel abonnement Pro ou Expert vous rapporte 15% de commission à vie.</p>
          
          <div className="flex items-center justify-center gap-2">
            <div className="rounded-lg border-2 border-dashed border-accent/50 bg-card px-6 py-3 font-mono text-2xl font-bold tracking-widest text-accent">
              {data.code}
            </div>
            <button onClick={copyCode} className="rounded-lg bg-surface p-3 text-muted hover:text-foreground transition-colors border border-border">
              {copied ? <Check className="h-5 w-5 text-success" /> : <Copy className="h-5 w-5" />}
            </button>
          </div>
          <button className="mt-4 mx-auto flex items-center gap-2 rounded-full bg-card border border-border px-4 py-2 text-sm font-medium hover:border-accent hover:text-accent transition-colors w-fit">
            <Share2 className="h-4 w-4" />Partager
          </button>
        </div>

        <div className="space-y-4">
          <div className="rounded-xl border border-border bg-card p-6">
            <h3 className="text-sm font-medium text-muted">Filleuls actifs</h3>
            <p className="mt-2 text-4xl font-bold">{data.nb_filleuls}</p>
          </div>
          <div className="rounded-xl border border-border bg-card p-6">
            <h3 className="text-sm font-medium text-muted">Commissions générées</h3>
            <p className="mt-2 text-4xl font-bold text-success">{formatDA(data.commission_totale_da)}</p>
            <button className="mt-4 text-xs font-medium text-accent hover:underline">Demander un retrait</button>
          </div>
        </div>
      </div>
    </div>
  );
}
