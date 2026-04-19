"use client";
// ============================================================
// Soumission DZ - Authenticated dashboard layout
// Collapsible sidebar + topbar
// ============================================================

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Shield,
  BookOpen,
  FileText,
  Calculator,
  Kanban,
  Headphones,
  CreditCard,
  LogOut,
  ChevronLeft,
  Zap,
  Menu,
  X,
  CheckCircle2,
  Activity,
  Briefcase,
  Users,
  LifeBuoy,
  Gift,
  Settings,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Tableau de bord", icon: LayoutDashboard },
  { href: "/dashboard/coffre", label: "Coffre-fort", icon: Shield },
  { href: "/dashboard/references", label: "Références", icon: BookOpen },
  { href: "/dashboard/ao", label: "Appels d'offres", icon: FileText },
  { href: "/dashboard/chiffrage", label: "Chiffrage", icon: Calculator },
  { href: "/dashboard/dossiers", label: "Dossiers", icon: Kanban },
  { href: "/dashboard/cautions", label: "Cautions", icon: CheckCircle2 },
  { href: "/dashboard/soumissions", label: "Historique", icon: Activity },
  { href: "/dashboard/portefeuille", label: "Portefeuille", icon: Briefcase },
  { href: "/dashboard/equipe", label: "Équipe", icon: Users },
  { href: "/dashboard/assistance", label: "Assistance", icon: Headphones },
  { href: "/dashboard/hotline", label: "Hotline", icon: LifeBuoy },
  { href: "/dashboard/facturation", label: "Facturation", icon: CreditCard },
  { href: "/dashboard/parrainage", label: "Parrainage", icon: Gift },
  { href: "/dashboard/admin", label: "Administration", icon: Settings },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [user, loading, router]);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 rounded-full border-2 border-accent border-t-transparent animate-spin" />
      </div>
    );
  }

  if (!user) return null;

  const isActive = (href: string) => {
    if (href === "/dashboard") return pathname === "/dashboard";
    return pathname.startsWith(href);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex flex-col border-r border-border bg-surface transition-all duration-300 lg:relative",
          "w-[240px]",
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        {/* Sidebar header */}
        <div className={cn(
          "flex h-14 items-center border-b border-border px-4",
          "justify-between"
        )}>
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-accent/10">
              <Zap className="h-4 w-4 text-accent" />
            </div>
            <span className="text-sm font-semibold tracking-tight">
              Soumission DZ
            </span>
          </Link>
          <button
            onClick={() => setMobileOpen(false)}
            className="lg:hidden text-muted-foreground hover:text-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Nav links */}
        <nav className="flex-1 overflow-y-auto p-2 space-y-0.5">
          {NAV_ITEMS.filter(item => {
            if (!user) return false;
            
            // ADMIN_PLATEFORME
            if (user.role === "ADMIN_PLATEFORME") {
              return ["Administration", "Tableau de bord"].includes(item.label);
            }
            
            // ASSISTANT_AGREE
            if (user.role === "ASSISTANT_AGREE") {
              return ["Assistance", "Tableau de bord"].includes(item.label);
            }

            // PATRON
            if (user.role === "PATRON") {
              if (item.label === "Administration") return false;
              if (item.label === "Portefeuille" && user.organisation_type !== "CABINET") return false;
              return true;
            }

            // CONSULTANT (CABINET)
            if (user.role === "CONSULTANT") {
              return ["Tableau de bord", "Portefeuille", "Dossiers", "AO", "Coffre-fort"].includes(item.label);
            }

            // AUDITEUR
            if (user.role === "AUDITEUR") {
              return ["Tableau de bord", "Appels d'offres", "Dossiers"].includes(item.label);
            }

            // PREPARATEUR
            if (user.role === "PREPARATEUR") {
              const hidden = ["Facturation", "Équipe", "Chiffrage", "Administration", "Portefeuille"];
              return !hidden.includes(item.label);
            }

            // Default fallback for CHEF_DOSSIER, VALIDATEUR, LECTEUR
            const hidden = ["Facturation", "Administration", "Portefeuille"];
            return !hidden.includes(item.label);
            
          }).map((item) => {
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all",
                  active
                    ? "bg-accent/10 text-accent font-medium"
                    : "text-muted hover:text-foreground hover:bg-card"
                )}
              >
                <item.icon className={cn("h-4 w-4 shrink-0", active && "text-accent")} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* User section */}
        <div className="border-t border-border p-2">
          <div className="mb-2 px-3 py-2">
            <p className="text-sm font-medium truncate">{user.username}</p>
            <p className="text-xs text-muted-foreground truncate">
              {user.organisation_nom}
            </p>
            <p className="mt-0.5 text-xs text-accent">{user.role}</p>
          </div>
          <button
            onClick={logout}
            className={cn(
              "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted hover:text-danger hover:bg-danger-muted transition-colors"
            )}
          >
            <LogOut className="h-4 w-4 shrink-0" />
            <span>Déconnexion</span>
          </button>
        </div>
      </aside>

      {/* Main content area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Topbar (mobile) */}
        <header className="flex h-14 items-center gap-4 border-b border-border px-4 lg:px-6">
          <button
            onClick={() => setMobileOpen(true)}
            className="lg:hidden text-muted-foreground hover:text-foreground"
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="flex-1" />

          <div className="flex items-center gap-3">
            <div className="hidden sm:block text-right">
              <p className="text-sm font-medium">{user.username}</p>
              <p className="text-xs text-muted-foreground">{user.plan_code}</p>
            </div>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/10 text-accent text-xs font-bold">
              {user.username.slice(0, 2).toUpperCase()}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-6xl px-4 py-6 lg:px-8 lg:py-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
