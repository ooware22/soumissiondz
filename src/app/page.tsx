import Link from "next/link";
import { Zap, Shield, Clock, BarChart3, FileText, ArrowRight, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

const FEATURES = [
  { icon: Shield, title: "Coffre-fort", desc: "15 types de documents officiels, alertes d'expiration automatiques" },
  { icon: BarChart3, title: "Audit 25 règles", desc: "Score de conformité sur 100 avec verdicts et suggestions" },
  { icon: FileText, title: "Génération DOCX", desc: "Mémoire technique et formulaires officiels en un clic" },
  { icon: Clock, title: "Gain de temps", desc: "De 8h à 2h par dossier. Zéro erreur de processus" },
];

const PLANS = [
  { name: "DÉCOUVERTE", price: "Gratuit", suffix: "(14 j)", target: "Test de la plateforme", highlight: false },
  { name: "ARTISAN", price: "5 000", suffix: "DA/mois", target: "TPE solo", highlight: false },
  { name: "PRO", price: "10 000", suffix: "DA/mois", target: "PME 5–30 employés", highlight: true },
  { name: "BUSINESS", price: "15 000", suffix: "DA/mois", target: "PME 30+, multi-utilisateurs", highlight: false },
  { name: "EXPERT", price: "20 000", suffix: "DA/mois", target: "Consultants multi-clients (Cas 2)", highlight: false },
  { name: "HOTLINE", price: "4 000", suffix: "DA/mois", target: "Add-on support (tous plans)", highlight: false },
];

export default function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Ambient background */}
      <div className="pointer-events-none fixed inset-0">
        <div className="absolute -left-[30%] -top-[30%] h-[70%] w-[70%] rounded-full bg-accent/[0.04] blur-[150px]" />
        <div className="absolute -bottom-[30%] -right-[30%] h-[60%] w-[60%] rounded-full bg-purple-500/[0.03] blur-[150px]" />
      </div>

      {/* Navbar */}
      <header className="relative z-10 flex items-center justify-between px-6 py-5 lg:px-12">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/10 border border-accent-border">
            <Zap className="h-4 w-4 text-accent" />
          </div>
          <span className="text-sm font-semibold tracking-tight">Soumission DZ</span>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/login" className="px-4 py-2 text-sm text-muted hover:text-foreground transition-colors">
            Connexion
          </Link>
          <Link href="/signup/entreprise" className="flex items-center gap-1.5 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-all hover:bg-accent-hover active:scale-[0.98]">
            Commencer
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="relative z-10 mx-auto max-w-5xl px-6 pt-24 pb-24 text-center lg:pt-36 lg:pb-36">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-accent/20 blur-[120px] rounded-full pointer-events-none" />
        
        <div className="animate-fade-in relative z-10">
          <h1 className="text-5xl font-extrabold tracking-tight sm:text-6xl lg:text-7xl">
            Remportez plus de marchés, <br className="hidden sm:block" />
            <span className="bg-gradient-to-r from-accent via-indigo-400 to-purple-400 bg-clip-text text-transparent drop-shadow-sm">
              avec zéro erreur de forme
            </span>
          </h1>
          
          <p className="mx-auto mt-8 max-w-2xl text-lg text-muted-foreground leading-relaxed sm:text-xl">
            La première plateforme SaaS dédiée aux marchés publics algériens. 
            Importez vos cahiers des charges, auditez votre dossier en 25 règles et générez votre offre en un clic.
          </p>
          
          <div className="mt-12 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link href="/signup/entreprise" className="group relative flex w-full items-center justify-center gap-2 rounded-full bg-accent px-8 py-4 text-sm font-bold text-white transition-all hover:bg-accent-hover hover:shadow-[0_0_40px_8px_rgba(var(--accent),0.3)] hover:-translate-y-0.5 active:scale-[0.98] sm:w-auto">
              Démarrer l'essai gratuit
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
            <Link href="/login" className="flex w-full items-center justify-center rounded-full border border-border bg-surface/50 px-8 py-4 text-sm font-semibold text-foreground backdrop-blur-sm transition-all hover:bg-card-hover hover:border-border-hover sm:w-auto">
              Voir la démo interactive
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="relative z-10 mx-auto max-w-5xl px-6 pb-24">
        <div className="stagger grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((f) => (
            <div key={f.title} className="group rounded-2xl border border-border bg-card p-6 transition-all hover:border-border-hover hover:bg-card-hover">
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-accent-muted">
                <f.icon className="h-5 w-5 text-accent" />
              </div>
              <h3 className="text-sm font-semibold">{f.title}</h3>
              <p className="mt-1.5 text-sm text-muted leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing preview */}
      <section className="relative z-10 mx-auto max-w-6xl px-6 pb-24 text-center">
        <h2 className="text-3xl font-bold tracking-tight">Des tarifs adaptés à votre structure</h2>
        <p className="mt-3 text-base text-muted-foreground">Une tarification transparente, sans frais cachés et sans engagement de durée.</p>
        
        <div className="stagger mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {PLANS.map((p) => (
            <div 
              key={p.name} 
              className={cn(
                "relative flex flex-col rounded-3xl border p-8 text-left transition-all duration-300",
                p.highlight 
                  ? "border-accent/50 bg-surface shadow-[0_0_30px_rgba(var(--accent),0.15)] scale-105 z-10" 
                  : "border-border bg-card hover:border-border-hover hover:bg-card-hover"
              )}
            >
              {p.highlight && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="rounded-full bg-accent px-4 py-1 text-xs font-bold uppercase tracking-wider text-white shadow-lg">
                    Le plus populaire
                  </span>
                </div>
              )}
              <h3 className={cn("text-sm font-bold tracking-wider", p.highlight ? "text-accent" : "text-muted-foreground")}>
                {p.name}
              </h3>
              <div className="mt-4 flex items-baseline gap-2">
                <span className="text-4xl font-extrabold tracking-tight text-foreground">{p.price}</span>
                <span className="text-sm font-medium text-muted-foreground">{p.suffix}</span>
              </div>
              <p className="mt-4 text-sm text-muted-foreground pb-6 border-b border-border/50">
                {p.target}
              </p>
              
              <div className="mt-6 flex-1">
                {/* Visual placeholder for features list */}
                <ul className="space-y-3">
                  <li className="flex items-center gap-3 text-sm text-muted"><CheckCircle2 className="h-4 w-4 text-accent" /> Accès coffre-fort</li>
                  <li className="flex items-center gap-3 text-sm text-muted"><CheckCircle2 className="h-4 w-4 text-accent" /> Audit 25 règles</li>
                  <li className="flex items-center gap-3 text-sm text-muted"><CheckCircle2 className="h-4 w-4 text-accent" /> Chiffrage & Simulation</li>
                </ul>
              </div>
              
              <button className={cn(
                "mt-8 w-full rounded-xl py-3 text-sm font-bold transition-all",
                p.highlight 
                  ? "bg-accent text-white hover:bg-accent-hover hover:shadow-lg hover:shadow-accent/25" 
                  : "bg-surface border border-border text-foreground hover:bg-card hover:border-border-hover"
              )}>
                Choisir ce plan
              </button>
            </div>
          ))}
        </div>
        
        <p className="mt-10 text-sm text-muted-foreground">
          Complément : <strong>Mode à l'acte 5 000 DA/dossier</strong>. Service d'assistance déléguée à partir de 8 000 DA.
        </p>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border px-6 py-8 text-center text-xs text-muted-foreground">
        <p>© 2026 Soumission DZ - Belhof. Hébergement Algérie. Conformité loi 18-07.</p>
      </footer>
    </div>
  );
}
