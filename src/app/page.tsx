import Link from "next/link";
import { Zap, Shield, Clock, BarChart3, FileText, ArrowRight, CheckCircle2 } from "lucide-react";

const FEATURES = [
  { icon: Shield, title: "Coffre-fort", desc: "15 types de documents officiels, alertes d'expiration automatiques" },
  { icon: BarChart3, title: "Audit 25 règles", desc: "Score de conformité sur 100 avec verdicts et suggestions" },
  { icon: FileText, title: "Génération DOCX", desc: "Mémoire technique et formulaires officiels en un clic" },
  { icon: Clock, title: "Gain de temps", desc: "De 8h à 2h par dossier. Zéro erreur de processus" },
];

const PLANS = [
  { name: "Artisan", price: "5 000", target: "TPE solo" },
  { name: "Pro", price: "10 000", target: "PME 5-30", popular: true },
  { name: "Business", price: "15 000", target: "PME 30+" },
  { name: "Expert", price: "20 000", target: "Cabinets" },
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
      <section className="relative z-10 mx-auto max-w-4xl px-6 pt-20 pb-24 text-center lg:pt-32 lg:pb-32">
        <div className="animate-fade-in">

          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
            <span className="bg-gradient-to-r from-foreground via-foreground to-muted bg-clip-text">
              Préparez vos dossiers
            </span>
            <br />
            <span className="bg-gradient-to-r from-accent via-purple-400 to-pink-400 bg-clip-text text-transparent">
              sans erreur
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-xl text-lg text-muted leading-relaxed">
            Plateforme SaaS pour les marchés publics algériens. 
            Importez un AO, auditez en 25 règles, générez le mémoire - déposez sereinement.
          </p>
          <div className="mt-10 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
            <Link href="/signup/entreprise" className="flex w-full items-center justify-center gap-2 rounded-xl bg-accent px-6 py-3 text-sm font-semibold text-white transition-all hover:bg-accent-hover hover:shadow-lg hover:shadow-accent/20 active:scale-[0.98] sm:w-auto">
              Essai gratuit 14 jours
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="/login" className="flex w-full items-center justify-center rounded-xl border border-border bg-card px-6 py-3 text-sm font-medium text-muted transition-all hover:text-foreground hover:border-border-hover sm:w-auto">
              Voir la démo
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
      <section className="relative z-10 mx-auto max-w-4xl px-6 pb-24 text-center">
        <h2 className="text-2xl font-semibold tracking-tight">Tarifs simples, en DA</h2>
        <p className="mt-2 text-sm text-muted">Pas de frais cachés. Annulation à tout moment.</p>
        <div className="stagger mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {PLANS.map((p) => (
            <div key={p.name} className={`rounded-2xl border p-6 text-left transition-all hover:border-border-hover ${p.popular ? "border-accent/30 bg-accent-muted glow-accent" : "border-border bg-card"}`}>
              {p.popular && <span className="mb-3 inline-block rounded-full bg-accent/20 px-2 py-0.5 text-xs font-medium text-accent">Populaire</span>}
              <h3 className="text-sm font-semibold">{p.name}</h3>
              <p className="mt-2"><span className="text-2xl font-bold">{p.price}</span><span className="text-sm text-muted"> DA/mois</span></p>
              <p className="mt-1 text-xs text-muted-foreground">{p.target}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border px-6 py-8 text-center text-xs text-muted-foreground">
        <p>© 2026 Soumission DZ - Belhof. Hébergement Algérie. Conformité loi 18-07.</p>
      </footer>
    </div>
  );
}
