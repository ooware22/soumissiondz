import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { AuthProvider } from "@/lib/auth";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "Marchés publics algériens",
    template: "%s | Soumission DZ",
  },
  description:
    "Plateforme SaaS d'aide à la préparation de dossiers de soumission aux marchés publics algériens. Gagnez du temps, évitez les erreurs.",
  keywords: [
    "soumission",
    "marchés publics",
    "Algérie",
    "BTPH",
    "appel d'offres",
    "DQE",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="fr"
      className={`${geistSans.variable} ${geistMono.variable} h-full`}
    >
      <body className="min-h-full bg-background text-foreground antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
