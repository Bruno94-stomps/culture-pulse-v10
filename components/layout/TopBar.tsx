"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { User } from "@supabase/supabase-js";
import { useRouter } from "next/navigation";
import LearningStatusWidget from "./LearningStatusWidget";
import { exportIntelligenceToPDF } from "@/lib/utils/pdf-export";
import { useExportDataContext } from "@/components/dashboard/ExportContext";
import useDashboardSupabaseClient from "@/components/dashboard/useDashboardSupabaseClient";

type Plan = "free" | "pro" | "executive" | "enterprise";

const PLAN_BADGE: Record<Plan, string> = {
  free:       "bg-gray-700 text-gray-300",
  pro:        "bg-violet-900/60 text-violet-300",
  executive:  "bg-blue-900/60 text-blue-300",
  enterprise: "bg-amber-900/60 text-amber-300",
};

export default function TopBar({ user, plan }: { user: User; plan: Plan }) {
  const pathname = usePathname();
  const router = useRouter();
  const { supabase } = useDashboardSupabaseClient();
  const { exportData } = useExportDataContext();
  const canExport = Boolean(exportData);

  async function handleLogout() {
    await supabase.auth.signOut();
    router.push("/login");
  }

  function handleExport() {
    if (!exportData) {
      alert("Acesse a página de Inteligência Cultural para gerar e exportar o relatório.");
      return;
    }

    exportIntelligenceToPDF(exportData);
  }

  return (
    <header className="h-14 bg-gray-950 border-b border-gray-800 flex items-center px-4 gap-2 shrink-0">
      {/* Logo */}
      <Link href="/dashboard" className="flex items-center gap-2 mr-6 shrink-0">
        <span className="text-lg font-extrabold text-white tracking-tight">
          Culture<span className="text-amber-400">Pulse</span>
        </span>
      </Link>

      {/* Left nav */}
      <nav className="hidden md:flex items-center gap-1">
        {[
          { href: "/dashboard",                 label: "Dashboard" },
          { href: "/dashboard/projects",        label: "Projetos"  },
          { href: "/dashboard/emerging-profiles", label: "Perfis" },
          { href: "/dashboard/strategy-learning", label: "Aprendizado" },
          { href: "/dashboard/system",          label: "Configuração" },
        ].map(({ href, label }) => {
          const active =
            href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                active
                  ? "bg-gray-800 text-white"
                  : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/50"
              }`}
            >
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Spacer */}
      <div className="flex-1 flex justify-center px-4">
        <LearningStatusWidget />
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Export Button (Only in Intelligence/Analytics if data is available) */}
        {pathname.includes("dashboard") && (
          <button
            onClick={handleExport}
            disabled={!canExport}
            title={canExport ? "Exportar relatório de Inteligência Cultural" : "Acesse Inteligência Cultural primeiro"}
            className={`hidden sm:flex items-center gap-1.5 h-8 px-3 border ${
              canExport
                ? "border-gray-800 hover:border-violet-500/50 text-gray-400 hover:text-white"
                : "border-gray-700 bg-gray-900 text-gray-500 cursor-not-allowed"
            } text-xs font-medium rounded-lg transition`}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            PDF
          </button>
        )}

        {/* New project */}
        <Link
          href="/dashboard/projects/new"
          className="flex items-center gap-1.5 h-8 px-3 bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium rounded-lg transition"
        >
          <span className="text-base leading-none font-light">+</span>
          <span className="hidden lg:inline">Novo Projeto</span>
        </Link>

        {/* Plan badge */}
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${PLAN_BADGE[plan]}`}>
          {plan.toUpperCase()}
        </span>

        {/* User avatar / settings */}
        <button
          onClick={handleLogout}
          className="w-8 h-8 rounded-full bg-violet-700 flex items-center justify-center text-white text-sm font-bold hover:bg-violet-600 transition"
          title={`${user.email ?? "Conta"} — clique para sair`}
        >
          {user.email?.[0].toUpperCase() ?? "?"}
        </button>
      </div>
    </header>
  );
}
