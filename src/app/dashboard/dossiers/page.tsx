"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { KanbanData, Dossier } from "@/lib/types";
import { Kanban, FileStack, ArrowRight, CheckCircle2, ChevronDown } from "lucide-react";

type ColumnDef = { key: string; label: string; color: string; bg: string };
type BoardDef = { id: string; title: string; columns: ColumnDef[] };

const BOARDS: BoardDef[] = [
  {
    id: "standard",
    title: "Workflow de traitement",
    columns: [
      { key: "a_faire", label: "À faire", color: "text-muted", bg: "bg-zinc-800" },
      { key: "en_cours", label: "En cours", color: "text-accent", bg: "bg-accent-muted" },
      { key: "a_valider", label: "À valider", color: "text-warning", bg: "bg-warning-muted" },
      { key: "termine", label: "Terminé", color: "text-success", bg: "bg-success-muted" },
    ]
  },
  {
    id: "phases",
    title: "Par phases du projet",
    columns: [
      { key: "prep", label: "Préparation & Docs", color: "text-purple-400", bg: "bg-purple-500/10" },
      { key: "etude", label: "Étude & Chiffrage", color: "text-sky-400", bg: "bg-sky-500/10" },
      { key: "depot", label: "Vérification & Dépôt", color: "text-orange-400", bg: "bg-orange-500/10" },
    ]
  },
  {
    id: "priorite",
    title: "Priorités de soumission",
    columns: [
      { key: "urgent", label: "Urgent (< 3j)", color: "text-danger", bg: "bg-danger-muted" },
      { key: "normal", label: "Normal", color: "text-accent", bg: "bg-accent-muted" },
      { key: "veille", label: "En veille", color: "text-muted", bg: "bg-zinc-800" },
    ]
  }
];

const ETAPE_LABELS: Record<string, string> = {
  profil: "Profil", documents: "Documents", audit: "Audit",
  chiffrage: "Chiffrage", memoire: "Mémoire", verification: "Vérification", depot: "Dépôt",
};

function DossierCard({ 
  d, colKey, onDragStart 
}: { 
  d: Dossier; colKey: string; onDragStart: (id: number, col: string) => void 
}) {
  return (
    <div 
      draggable
      onDragStart={(e) => {
        e.dataTransfer.setData("text/plain", d.id.toString());
        onDragStart(d.id, colKey);
      }}
      className="rounded-lg border border-border bg-surface p-3.5 hover:border-border-hover transition-colors cursor-grab active:cursor-grabbing group shadow-sm"
    >
      <p className="text-sm font-medium group-hover:text-accent transition-colors">{d.nom}</p>
      <div className="mt-2 flex items-center justify-between">
        <span className="rounded-md bg-card px-2 py-0.5 text-[11px] text-muted-foreground border border-border">
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
  const [activeBoardId, setActiveBoardId] = useState(BOARDS[0].id);
  const activeBoard = BOARDS.find(b => b.id === activeBoardId)!;
  const [allDossiers, setAllDossiers] = useState<Dossier[]>([]);
  const [data, setData] = useState<KanbanData | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Drag and Drop State
  const [draggedItem, setDraggedItem] = useState<{ id: number; sourceCol: string } | null>(null);
  const [dragOverCol, setDragOverCol] = useState<string | null>(null);

  // Initial load
  useEffect(() => {
    apiGet<KanbanData>("/dossiers/kanban")
      .then(res => {
        // Flatten mock data into a single pool for the dynamic views demonstration
        const pool = Object.values(res).flat();
        setAllDossiers(pool);
        distributeDossiers(pool, BOARDS[0]);
      })
      .catch(() => {
        setAllDossiers([]);
        distributeDossiers([], BOARDS[0]);
      })
      .finally(() => setLoading(false));
  }, []);

  // On board switch
  useEffect(() => {
    if (allDossiers.length > 0) {
      distributeDossiers(allDossiers, activeBoard);
    }
  }, [activeBoardId]);

  const distributeDossiers = (pool: Dossier[], board: BoardDef) => {
    const newData: KanbanData = {};
    board.columns.forEach(c => newData[c.key] = []);
    // Simple distribution strategy based on the index to show cards across columns
    pool.forEach((d, i) => {
      const colIndex = i % board.columns.length;
      newData[board.columns[colIndex].key].push(d);
    });
    setData(newData);
  };

  const total = allDossiers.length;

  const handleDrop = (e: React.DragEvent, targetCol: string) => {
    e.preventDefault();
    setDragOverCol(null);
    if (!draggedItem || !data || draggedItem.sourceCol === targetCol) return;

    setData(prev => {
      if (!prev) return prev;
      const sourceList = [...prev[draggedItem.sourceCol]];
      const destList = [...prev[targetCol]];
      
      const itemIndex = sourceList.findIndex(x => x.id === draggedItem.id);
      if (itemIndex === -1) return prev;
      
      const [item] = sourceList.splice(itemIndex, 1);
      destList.push(item);
      
      return { ...prev, [draggedItem.sourceCol]: sourceList, [targetCol]: destList };
    });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
            <Kanban className="h-6 w-6 text-orange-400" />
            Dossiers de soumission
          </h1>
          <p className="mt-1 text-sm text-muted">
            {total} dossier{total !== 1 ? "s" : ""} en cours de traitement.
          </p>
        </div>

        {/* Board View Selector */}
        <div className="relative inline-block w-full sm:w-64">
          <select 
            value={activeBoardId} 
            onChange={e => setActiveBoardId(e.target.value)}
            className="w-full appearance-none rounded-xl border border-border bg-card px-4 py-2.5 text-sm font-medium focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
          >
            {BOARDS.map(b => (
              <option key={b.id} value={b.id}>Vue : {b.title}</option>
            ))}
          </select>
          <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        </div>
      </div>

      {/* Pipeline legend */}
      <div className="flex items-center gap-1 text-xs text-muted-foreground overflow-x-auto pb-1">
        {Object.keys(ETAPE_LABELS).map((e, i, arr) => (
          <span key={e} className="flex items-center gap-1 whitespace-nowrap">
            <span className="rounded bg-card px-1.5 py-0.5 border border-border">{ETAPE_LABELS[e]}</span>
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
        <div className="flex overflow-x-auto pb-4 -mx-4 px-4 sm:mx-0 sm:px-0 scrollbar-hide">
          <div className="flex gap-4 min-w-max">
            {activeBoard.columns.map(col => (
              <div 
                key={col.key} 
                onDragOver={(e) => { e.preventDefault(); setDragOverCol(col.key); }}
                onDragLeave={() => setDragOverCol(null)}
                onDrop={(e) => handleDrop(e, col.key)}
                className={cn(
                  "flex flex-col rounded-xl border bg-card w-[320px] min-h-[400px] transition-colors duration-200",
                  dragOverCol === col.key ? "border-accent/50 bg-accent/5 shadow-[0_0_15px_rgba(var(--accent),0.1)]" : "border-border"
                )}
              >
                <div className="flex items-center justify-between border-b border-border/50 px-4 py-3 bg-surface/50 rounded-t-xl">
                  <span className={cn("text-sm font-semibold", col.color)}>{col.label}</span>
                  <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", col.bg, col.color)}>
                    {data[col.key] ? data[col.key].length : 0}
                  </span>
                </div>
                <div className="flex-1 p-3 space-y-3 overflow-y-auto">
                  {!data[col.key] || data[col.key].length === 0 ? (
                    <div className="flex h-full items-center justify-center">
                      <div className="flex flex-col items-center gap-2 text-muted-foreground/30">
                        <FileStack className="h-8 w-8" />
                        <span className="text-xs font-medium">Glisser ici</span>
                      </div>
                    </div>
                  ) : (
                    data[col.key].map(d => (
                      <DossierCard 
                        key={d.id} 
                        d={d} 
                        colKey={col.key} 
                        onDragStart={(id, sourceCol) => setDraggedItem({ id, sourceCol })} 
                      />
                    ))
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
