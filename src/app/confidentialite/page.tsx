import Link from "next/link";
import { Shield } from "lucide-react";

export const metadata = { title: "Confidentialité | Soumission DZ" };

export default function ConfidentialitePage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center px-6">
          <Link href="/" className="flex items-center gap-2 font-bold tracking-tight text-white transition-opacity hover:opacity-80">
            <Shield className="h-5 w-5 text-accent" />Soumission DZ
          </Link>
        </div>
      </header>
      
      <main className="mx-auto max-w-3xl px-6 py-16">
        <h1 className="text-4xl font-bold mb-8">Politique de Confidentialité</h1>
        
        <div className="prose prose-invert prose-emerald max-w-none space-y-6 text-muted-foreground">
          <p>Dernière mise à jour : 18 Avril 2026</p>
          
          <div className="rounded-xl border border-accent/20 bg-accent-muted/10 p-6">
            <h2 className="text-xl font-semibold text-white mt-0">Conformité Loi 18-07</h2>
            <p className="text-sm mt-2">
              Conformément à la Loi n° 18-07 du 10 juin 2018 relative à la protection des personnes physiques dans le traitement des données à caractère personnel, Soumission DZ s&apos;engage à protéger vos données.
            </p>
          </div>

          <h3 className="text-xl font-semibold text-white">1. Données collectées</h3>
          <p>Nous collectons les données suivantes : informations d&apos;identification de l&apos;entreprise (NIF, NIS, RC), documents administratifs téléchargés dans le coffre-fort, historique des soumissions et tarifs proposés.</p>

          <h3 className="text-xl font-semibold text-white">2. Hébergement en Algérie</h3>
          <p>Toutes nos infrastructures serveurs et bases de données sont physiquement hébergées sur le territoire national algérien, garantissant la souveraineté de vos données commerciales sensibles.</p>

          <h3 className="text-xl font-semibold text-white">3. Cloisonnement (Isolation des locataires)</h3>
          <p>Notre architecture garantit une isolation stricte. Les données d&apos;une entreprise ne peuvent en aucun cas être croisées ou consultées par une autre entité.</p>

          <h3 className="text-xl font-semibold text-white">4. Droit d&apos;export et de suppression</h3>
          <p>Vous disposez d&apos;un droit d&apos;accès, de rectification et de suppression. Vous pouvez exporter l&apos;intégralité de vos données (Archive ZIP) ou demander la suppression définitive (Purge J+30) directement depuis votre espace client.</p>

          <div className="mt-12 pt-8 border-t border-border">
            <p className="text-sm text-center">Pour toute question, contactez notre DPO : dpo@soumission.dz</p>
          </div>
        </div>
      </main>
    </div>
  );
}
