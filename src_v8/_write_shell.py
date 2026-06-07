#!/usr/bin/env python3
"""Temp script to write DashboardShell.tsx and TopBar.tsx with proper UTF-8."""

import os

SHELL_PATH = "/Users/brmunizmoura/Documents/PULSO/culturepulse-web/components/dashboard/DashboardShell.tsx"

shell_content = '''"use client";

import type { User } from "@supabase/supabase-js";
import Link from "next/link";
import { usePathname } from "next/navigation";
import TopBar from "@/components/layout/TopBar";

type Plan = "free" | "pro" | "executive" | "enterprise";

const EXPLORE_ITEMS = [
  { href: "/dashboard/explore/sectors", label: "\U0001f3ed Setores" },
  { href: "/dashboard/explore/themes", label: "\U0001f50d Temas" },
  { href: "/dashboard/explore/brands", label: "\U0001f3f7\ufe0f Marcas" },
  { href: "/dashboard/explore/territories", label: "\U0001f5fa\ufe0f Territ\u00f3rios" },
];

const DASHBOARD_ITEMS = [
  { href: "/dashboard", label: "\U0001f4ca Vis\u00e3o Geral" },
  { href: "/dashboard/projects", label: "\U0001f4c1 Projetos" },
  { href: "/dashboard/signals", label: "\U0001f4e1 Sinais" },
  { href: "/dashboard/circles", label: "\U0001f535 C\u00edrculos" },
  { href: "/dashboard/unknowns", label: "\U0001f195 Emergentes" },
  { href: "/dashboard/stability-risk", label: "\u2696\ufe0f Estab. \u00d7 Risco" },
  { href: "/dashboard/trends", label: "\U0001f4c8 Tend\u00eancias" },
  { href: "/dashboard/intelligence", label: "\U0001f6e1\ufe0f Intelig\u00eancia" },
  { href: "/dashboard/alma", label: "\U0001f1e7\U0001f1f7 Alma Brasileira" },
  { href: "/dashboard/analytics", label: "\U0001f4ca Analytics" },
  { href: "/dashboard/enterprise", label: "\U0001f3e2 Enterprise" },
];

export default function DashboardShell({
  user,
  plan,
  children,
}: {
  user: User;
  plan: Plan;
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <TopBar user={user} plan={plan} />

      <div className="flex flex-1 overflow-hidden">
        <aside className="w-56 bg-white border-r border-gray-200 flex flex-col shrink-0">
          <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
            {/* Explore section */}
            <p className="px-3 pt-2 pb-1 text-[10px] font-bold text-gray-400 uppercase tracking-wider">
              Explorar
            </p>
            {EXPLORE_ITEMS.map(({ href, label }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  className={`flex items-center px-3 py-2 rounded-lg text-xs font-medium transition ${
                    active
                      ? "bg-violet-50 text-violet-700"
                      : "text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {label}
                </Link>
              );
            })}

            {/* Divider */}
            <div className="!my-2 border-t border-gray-100" />

            {/* Main nav */}
            <p className="px-3 pt-1 pb-1 text-[10px] font-bold text-gray-400 uppercase tracking-wider">
              Dashboard
            </p>
            {DASHBOARD_ITEMS.map(({ href, label }) => {
              const active =
                href === "/dashboard"
                  ? pathname === "/dashboard"
                  : pathname.startsWith(href);
              return (
                <Link
                  key={href}
                  href={href}
                  className={`flex items-center px-3 py-2 rounded-lg text-xs font-medium transition ${
                    active
                      ? "bg-violet-50 text-violet-700"
                      : "text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {label}
                </Link>
              );
            })}
          </nav>
        </aside>

        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
'''

with open(SHELL_PATH, 'w', encoding='utf-8') as f:
    f.write(shell_content)
print(f"Wrote DashboardShell.tsx ({len(shell_content)} chars)")

# Also fix TopBar - keep it clean
TOPBAR_PATH = "/Users/brmunizmoura/Documents/PULSO/culturepulse-web/components/layout/TopBar.tsx"

topbar_content = '''"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { User } from "@supabase/supabase-js";
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import { useState } from "react";

type Plan = "free" | "pro" | "executive" | "enterprise";

const TOP_NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/dashboard/explore/sectors", label: "Explorar" },
  { href: "/dashboard/projects", label: "Projects" },
  { href: "/dashboard/signals", label: "Signals" },
  { href: "/dashboard/analytics", label: "Analytics" },
];

const PLAN_BADGE: Record<Plan, string> = {
  free: "bg-gray-700 text-gray-300",
  pro: "bg-violet-900/60 text-violet-300",
  executive: "bg-blue-900/60 text-blue-300",
  enterprise: "bg-amber-900/60 text-amber-300",
};

export default function TopBar({ user, plan }: { user: User; plan: Plan }) {
  const pathname = usePathname();
  const router = useRouter();
  const supabase = createClient();
  const [searchQuery, setSearchQuery] = useState("");

  async function handleLogout() {
    await supabase.auth.signOut();
    router.push("/login");
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/dashboard/signals?search=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery("");
    }
  }

  return (
    <header className="h-14 bg-gray-950 border-b border-gray-800 flex items-center px-4 gap-2 shrink-0">
      {/* Logo */}
      <Link href="/dashboard" className="flex items-center gap-2 mr-6">
        <span className="text-lg font-extrabold text-white tracking-tight">
          Culture<span className="text-amber-400">Pulse</span>
        </span>
      </Link>

      {/* Nav links */}
      <nav className="hidden md:flex items-center gap-1">
        {TOP_NAV.map(({ href, label }) => {
          const active =
            (label === "Dashboard" && pathname === "/dashboard") ||
            (label === "Explorar" && pathname.startsWith("/dashboard/explore")) ||
            (label !== "Dashboard" && label !== "Explorar" && pathname.startsWith(href));
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
      <div className="flex-1" />

      {/* Search */}
      <form onSubmit={handleSearch} className="hidden sm:flex items-center">
        <div className="relative">
          <input
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-48 lg:w-64 h-8 bg-gray-800 border border-gray-700 rounded-lg px-3 pr-8 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition"
          />
          <svg className="absolute right-2.5 top-2 w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </form>

      {/* + New Project */}
      <Link
        href="/dashboard/projects/new"
        className="flex items-center gap-1.5 h-8 px-3 bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium rounded-lg transition ml-2"
      >
        <span className="text-lg leading-none">+</span>
        <span className="hidden lg:inline">New Project</span>
      </Link>

      {/* User avatar + plan */}
      <div className="flex items-center gap-2 ml-3">
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${PLAN_BADGE[plan]}`}>
          {plan.toUpperCase()}
        </span>
        <button
          onClick={handleLogout}
          className="w-8 h-8 rounded-full bg-violet-700 flex items-center justify-center text-white text-sm font-bold hover:bg-violet-600 transition"
          title={user.email ?? "Sair"}
        >
          {user.email?.[0].toUpperCase() ?? "?"}
        </button>
      </div>
    </header>
  );
}
'''

with open(TOPBAR_PATH, 'w', encoding='utf-8') as f:
    f.write(topbar_content)
print(f"Wrote TopBar.tsx ({len(topbar_content)} chars)")
