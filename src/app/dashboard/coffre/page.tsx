"use client";

import { useEffect, useState, useCallback } from "react";
import { apiGet, apiUpload, apiDelete } from "@/lib/api";
import { formatFileSize, formatDateShort, cn } from "@/lib/utils";
import type { Document, DocumentType, AlerteExpiration } from "@/lib/types";
import { Shield, Upload, Trash2, Download, AlertTriangle, Plus, X, Loader2, FileText } from "lucide-react";

export default function CoffrePage() {
  const [docs, setDocs] = useState<Document[]>([]);
  const [types, setTypes] = useState<DocumentType[]>([]);
  const [alertes, setAlertes] = useState<AlerteExpiration[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [typeCode, setTypeCode] = useState("");
  const [dateExp, setDateExp] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const load = useCallback(async () => {
    const [d, t, a] = await Promise.all([
      apiGet<Document[]>("/coffre/documents").catch(() => []),
      apiGet<DocumentType[]>("/coffre/types").catch(() => []),
      apiGet<AlerteExpiration[]>("/coffre/alertes").catch(() => []),
    ]);
    setDocs(d); setTypes(t); setAlertes(a);
    if (t.length && !typeCode) setTypeCode(t[0].code);
    setLoading(false);
  }, [typeCode]);

  useEffect(() => { load(); }, [load]);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("type_code", typeCode);
      fd.append("file", file);
      if (dateExp) fd.append("date_expiration", dateExp);
      await apiUpload("/coffre/documents", fd);
      setShowUpload(false); setFile(null); setDateExp("");
      await load();
    } catch { /* toast */ }
    setUploading(false);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Supprimer ce document ?")) return;
    await apiDelete(`/coffre/documents/${id}`);
    await load();
  };

  const inputCls = "w-full rounded-lg border border-border bg-input px-3 py-2.5 text-sm text-foreground transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/50";

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
            <Shield className="h-6 w-6 text-accent" />
            Coffre-fort documentaire
          </h1>
          <p className="mt-1 text-sm text-muted">Gérez vos documents officiels et suivez leurs expirations.</p>
        </div>
        <button onClick={() => setShowUpload(!showUpload)} className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-accent-hover active:scale-[0.98]">
          {showUpload ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showUpload ? "Annuler" : "Ajouter"}
        </button>
      </div>

      {/* Upload form */}
      {showUpload && (
        <div className="rounded-xl border border-accent-border bg-accent-muted/30 p-5 animate-fade-in-scale">
          <form onSubmit={handleUpload} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Type de document</label>
                <select value={typeCode} onChange={(e) => setTypeCode(e.target.value)} className={inputCls}>
                  {types.map((t) => <option key={t.code} value={t.code}>{t.code} - {t.libelle}</option>)}
                </select>
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Date d&apos;expiration</label>
                <input type="date" value={dateExp} onChange={(e) => setDateExp(e.target.value)} className={inputCls} />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted">Fichier PDF</label>
                <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} className={inputCls} />
              </div>
            </div>
            <button type="submit" disabled={!file || uploading} className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-accent-hover disabled:opacity-50">
              {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
              Uploader
            </button>
          </form>
        </div>
      )}

      {/* Alerts */}
      {alertes.length > 0 && (
        <div className="rounded-xl border border-warning/20 bg-warning-muted/30 p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="h-4 w-4 text-warning" />
            <span className="text-sm font-semibold text-warning">{alertes.length} alerte(s) d&apos;expiration</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {alertes.map((a, i) => (
              <span key={i} className={cn("rounded-full px-2.5 py-1 text-xs font-medium",
                a.seuil === "expire" || a.seuil === "7j" ? "bg-danger-muted text-danger" : "bg-warning-muted text-warning"
              )}>
                {a.type_code} - {a.jours_restants < 0 ? "Expiré" : `${a.jours_restants}j`}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Documents table */}
      {loading ? (
        <div className="space-y-3">
          {[1,2,3].map(i => <div key={i} className="skeleton h-14 w-full" />)}
        </div>
      ) : docs.length === 0 ? (
        <div className="rounded-xl border border-border bg-card p-12 text-center">
          <FileText className="mx-auto h-10 w-10 text-muted-foreground/40 mb-3" />
          <p className="text-sm text-muted">Aucun document. Cliquez sur &quot;Ajouter&quot; pour uploader votre premier document.</p>
        </div>
      ) : (
        <div className="rounded-xl border border-border bg-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                {["Type", "Fichier", "Taille", "Expiration", ""].map(h => (
                  <th key={h} className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {docs.map(d => (
                <tr key={d.id} className="border-b border-border/50 last:border-0 hover:bg-card-hover transition-colors">
                  <td className="px-5 py-3"><span className="rounded-md bg-accent-muted px-2 py-0.5 text-xs font-medium text-accent">{d.type_code}</span></td>
                  <td className="px-5 py-3 font-medium">{d.filename}</td>
                  <td className="px-5 py-3 text-muted">{formatFileSize(d.size_bytes)}</td>
                  <td className="px-5 py-3 text-muted">{d.date_expiration ? formatDateShort(d.date_expiration) : "-"}</td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-1.5 justify-end">
                      <a href={`/coffre/documents/${d.id}/download`} className="rounded-md p-1.5 text-muted-foreground hover:text-foreground hover:bg-card transition-colors" title="Télécharger">
                        <Download className="h-4 w-4" />
                      </a>
                      <button onClick={() => handleDelete(d.id)} className="rounded-md p-1.5 text-muted-foreground hover:text-danger hover:bg-danger-muted transition-colors" title="Supprimer">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
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
