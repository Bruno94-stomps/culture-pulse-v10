import { createClient } from "@/lib/supabase/server";
import { getCurrentPlan } from "@/lib/plan";
import Link from "next/link";

export const revalidate = 0; // always fresh

interface Project {
  id: string;
  name: string;
  brand: string;
  keywords: string[];
  segment: string;
  status: "draft" | "collecting" | "analyzing" | "ready" | "error";
  signals_count: number;
  circles: string[];
  created_at: string;
  last_analysis_at: string | null;
}

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  draft:      { label: "Rascunho",   color: "bg-gray-100 text-gray-600",    icon: "📝" },
  collecting: { label: "Coletando",  color: "bg-blue-100 text-blue-700",    icon: "🔄" },
  analyzing:  { label: "Analisando", color: "bg-violet-100 text-violet-700", icon: "🧠" },
  ready:      { label: "Pronto",     color: "bg-green-100 text-green-700",   icon: "✅" },
  error:      { label: "Erro",       color: "bg-red-100 text-red-700",       icon: "❌" },
};

export default async function ProjectsPage() {
  const supabase = createClient();
  const plan = await getCurrentPlan();

  const limits: Record<string, number> = { free: 1, pro: 5, executive: 20, enterprise: 999 };
  const maxProjects = limits[plan] ?? 1;

  let projects: Project[] = [];
  let migrationNeeded = false;

  try {
    const { data, error } = await supabase
      .from("projects")
      .select("*")
      .order("created_at", { ascending: false });

    if (error && error.message.includes("Could not find")) {
      migrationNeeded = true;
    } else {
      projects = (data ?? []) as Project[];
    }
  } catch {
    migrationNeeded = true;
  }

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">📁 Projetos</h1>
          <p className="text-gray-500 text-sm mt-0.5">
            {projects.length} de {maxProjects} projetos · Plano {plan.toUpperCase()}
          </p>
        </div>
        <Link
          href="/dashboard/projects/new"
          className="flex items-center gap-2 h-10 px-5 bg-violet-600 hover:bg-violet-500 text-white text-sm font-semibold rounded-xl transition shadow-sm"
        >
          <span className="text-lg">+</span>
          Novo Projeto
        </Link>
      </div>

      {/* Migration notice */}
      {migrationNeeded && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <p className="text-sm text-amber-800 font-medium">⚠️ Tabela `projects` não encontrada no Supabase.</p>
          <p className="text-xs text-amber-600 mt-1">
            Execute o SQL em <code className="bg-amber-100 px-1 rounded">supabase/migrations/20260224_create_projects.sql</code> no SQL Editor do Supabase.
          </p>
        </div>
      )}

      {/* Empty state */}
      {!migrationNeeded && projects.length === 0 && (
        <div className="text-center py-16 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <p className="text-5xl mb-4">🚀</p>
          <h2 className="text-xl font-bold text-gray-800">Nenhum projeto ainda</h2>
          <p className="text-sm text-gray-500 mt-1 max-w-md mx-auto">
            Crie seu primeiro projeto de análise cultural. Defina a marca, keywords do briefing e deixe nossos 18 engines fazerem o trabalho.
          </p>
          <Link
            href="/dashboard/projects/new"
            className="inline-flex items-center gap-2 mt-6 px-6 py-3 bg-violet-600 hover:bg-violet-500 text-white font-semibold rounded-xl transition"
          >
            + Criar Primeiro Projeto
          </Link>
        </div>
      )}

      {/* Project cards */}
      {projects.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((p) => {
            const st = STATUS_CONFIG[p.status] ?? STATUS_CONFIG.draft;
            return (
              <Link
                key={p.id}
                href={`/dashboard/projects/${p.id}`}
                className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:border-violet-200 hover:shadow-md transition group"
              >
                {/* Status badge */}
                <div className="flex items-center justify-between mb-3">
                  <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${st.color}`}>
                    {st.icon} {st.label}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(p.created_at).toLocaleDateString("pt-BR")}
                  </span>
                </div>

                {/* Name + brand */}
                <h3 className="text-sm font-bold text-gray-800 group-hover:text-violet-700 transition">
                  {p.name}
                </h3>
                <p className="text-xs text-gray-500 mt-0.5">🏷️ {p.brand} · {p.segment}</p>

                {/* Keywords */}
                <div className="flex flex-wrap gap-1 mt-3">
                  {p.keywords.slice(0, 4).map((kw, i) => (
                    <span key={i} className="text-[10px] bg-violet-50 text-violet-600 px-2 py-0.5 rounded-full">
                      {kw}
                    </span>
                  ))}
                  {p.keywords.length > 4 && (
                    <span className="text-[10px] text-gray-400">+{p.keywords.length - 4}</span>
                  )}
                </div>

                {/* Metrics footer */}
                <div className="flex items-center gap-4 mt-4 pt-3 border-t border-gray-50">
                  <div className="text-xs text-gray-500">
                    <span className="font-bold text-gray-700">{p.signals_count}</span> sinais
                  </div>
                  <div className="text-xs text-gray-500">
                    <span className="font-bold text-gray-700">{p.circles.length}</span> círculos
                  </div>
                  {p.last_analysis_at && (
                    <div className="text-xs text-gray-400 ml-auto">
                      🕐 {new Date(p.last_analysis_at).toLocaleDateString("pt-BR")}
                    </div>
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
