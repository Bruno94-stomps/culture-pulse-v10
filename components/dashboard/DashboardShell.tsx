"use client";

import type { User } from "@supabase/supabase-js";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import TopBar from "../layout/TopBar";
import ConversationalPrompt from "../intelligence/ConversationalPrompt";
import { ExportProvider } from "./ExportContext";
import { DashboardProvider, type Plan } from "./DashboardContext";

// ─── Sidebar groups ───────────────────────────────────────────────────────────
const SIDEBAR_GROUPS = [
	{
		label: "Core",
		items: [
			{ href: "/dashboard/signals", label: "Sinais & Estabilidade" },
			{ href: "/dashboard/insights", label: "Insights" },
			{ href: "/dashboard/trends", label: "Tendencias" },
			{ href: "/dashboard/alma", label: "Alma Brasileira" },
			{ href: "/dashboard/alerts", label: "Alertas & SOS" },
		],
	},
	{
		label: "Deep Analysis",
		items: [
			{ href: "/dashboard/circles", label: "Círculos Culturais" },
			{ href: "/dashboard/clustering", label: "Mapas & Agrupamentos" },
			{ href: "/dashboard/emerging-profiles", label: "Perfis Emergentes" },
			{ href: "/dashboard/strategy-learning", label: "Aprendizado" },
			{ href: "/dashboard/unknowns", label: "Desconhecido Emergente" },
		],
	},
	{
		label: "Configuracao",
		items: [
			{ href: "/dashboard/system", label: "Status do Sistema" },
			{ href: "/dashboard/analytics", label: "Analytics V9" },
		],
	},
];

// ─── Collapsible group ────────────────────────────────────────────────────────
function SidebarGroup({
	label,
	items,
	pathname,
}: {
	label: string;
	items: { href: string; label: string }[];
	pathname: string;
}) {
	const isGroupActive = items.some((i) => pathname.startsWith(i.href));
	const [open, setOpen] = useState(isGroupActive);

	return (
		<div className="mb-0.5">
			<button
				onClick={() => setOpen((v) => !v)}
				className="w-full flex items-center justify-between px-3 py-1.5 text-[10px] font-bold text-gray-400 uppercase tracking-wider hover:text-gray-300 transition"
			>
				<span>{label}</span>
				<svg
					className={
						"w-3 h-3 transition-transform duration-200 " +
						(open ? "rotate-180" : "")
					}
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						strokeLinecap="round"
						strokeLinejoin="round"
						strokeWidth={2.5}
						d="M19 9l-7 7-7-7"
					/>
				</svg>
			</button>

			{open && (
				<div className="ml-2 space-y-0.5 mb-1">
					{items.map(({ href, label: itemLabel }) => {
						const active = pathname.startsWith(href);
						return (
							<Link
								key={href}
								href={href}
								className={
									"flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition " +
									(active
										? "bg-violet-50 text-violet-700"
										: "text-gray-500 hover:bg-gray-50 hover:text-gray-700")
								}
							>
								<span
									className={
										"w-1 h-1 rounded-full shrink-0 " +
										(active ? "bg-violet-500" : "bg-gray-300")
									}
								/>
								{itemLabel}
							</Link>
						);
					})}
				</div>
			)}
		</div>
	);
}

// ─── Shell ────────────────────────────────────────────────────────────────────
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
		<DashboardProvider user={user} plan={plan}>
			<ExportProvider>
				<div className="flex flex-col h-screen bg-gray-50">
					<TopBar user={user} plan={plan} />

				<div className="flex flex-1 overflow-hidden">
					<aside className="w-52 bg-white border-r border-gray-200 flex flex-col shrink-0">
						<nav className="flex-1 px-2 py-3 overflow-y-auto">
							{SIDEBAR_GROUPS.map((group) => (
								<SidebarGroup
									key={group.label}
									label={group.label}
									items={group.items}
									pathname={pathname}
								/>
							))}
						</nav>

						<div className="px-4 py-3 border-t border-gray-100">
							<p className="text-[10px] text-gray-400 truncate">
								Culture
								<span className="text-amber-500">Pulse</span> v9
							</p>
						</div>
					</aside>

					<main className="flex-1 overflow-y-auto">{children}</main>
				</div>

				{/* Componente de Active Learning Conversacional (V9.7) */}
				<ConversationalPrompt />
			</div>
		</ExportProvider>
		</DashboardProvider>
	);
}
