import { createClient } from "@/lib/supabase/server";
import SignalsTable from "@/components/signals/SignalsTable";
import ConversationalPrompt from "@/components/intelligence/ConversationalPrompt";
import { 
  Activity, 
  Zap, 
  TrendingUp, 
  MessageCircle, 
  Sparkles,
  Filter,
  ArrowRight
} from "lucide-react";

/** Tipos espelhando o schema do Supabase */
export interface CulturalSignal {
  id: number;
  tipo: string;
  circulo: string;
  termo: string;
  score: number;
  regiao: string;
  plataforma: string;
  raw_data: {
    momentum?: number;
    momentum_velocity?: number; // V9.6: Aceleração
    volume?: number;
    sentiment?: number;
    tension_score?: number;     // V9.6: Matriz de Tensão
    cultural_relevance?: number;
    authenticity_score?: number; // V9.6: Score de Autenticidade
    weak_signal_score?: number;
    rareness_score?: number;
    campaign_fit?: number;      // V9.6: Campaign Match
    context_tags?: string[];    // V9.6: Mapa de Calor contextuais
    is_verified_source?: boolean;
    visual_proof_score?: number;
    weak_signal_badge?: string | null;
    volume_spike?: boolean;
    sentiment_shift?: boolean;
    context_anomaly?: boolean;
    explicacao?: string;
    is_verified?: boolean;      // V9.9: Veracidade
    reliability?: string;       // V9.9: Veracidade
    accuracy_score?: number;    // V9.9: Veracidade
    visual_proof?: boolean;     // V9.9: Veracidade
    cross_verified?: boolean;   // V9.9: Veracidade
    thumbnail?: string;         // V9.9: Veracidade
    image_url?: string;         // V9.9: Veracidade
    url?: string;               // V9.9: Veracidade
    calculation_details?: any;  // V9.9: Veracidade
    narrativa_cultural?: string; // V9.9: IA Local (Llama-3)
    recomendacao_acao?: string;  // V9.9: IA Local (Llama-3)
    using_local_slm?: boolean;   // V9.9: IA Local (Llama-3)
    evidence?: Array<{
      url: string;
      thumbnail: string;
      title: string;
      platform: string;
      channel: string;
      published_at: string;
    }>;
  };
  ts: string;
  is_verified?: boolean;
  reliability?: string;
  accuracy_score?: number;
  visual_proof?: boolean;
  cross_verified?: boolean;
  thumbnail?: string;
  image_url?: string;
  url?: string;
}

export const revalidate = 60; // revalida a cada 60s (ISR)

interface PageProps {
  searchParams: Promise<{ circulo?: string; tipo?: string; minScore?: string }>;
}

export default async function SignalsPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const supabase = createClient();

  // ── Query com filtros opcionais ──────────────────────────────────────────
  let query = supabase
    .from("cultural_signals")
    .select("id, tipo, circulo, termo, score, regiao, plataforma, raw_data, ts")
    .order("ts", { ascending: false })
    .limit(200);

  if (params.circulo && params.circulo !== "todos") {
    query = query.eq("circulo", params.circulo);
  }
  if (params.tipo && params.tipo !== "todos") {
    query = query.eq("tipo", params.tipo);
  }
  if (params.minScore) {
    query = query.gte("score", parseFloat(params.minScore));
  }

  const { data: signals, error } = await query;

  const effectiveSignals = signals ?? [];

  // ── Unknown circles (emergente_desconhecido) ────────────────────────────
  const { count: unknownCount } = await supabase
    .from("cultural_signals")
    .select("id", { count: "exact", head: true })
    .eq("circulo", "emergente_desconhecido");

  const { data: unknownSignals } = await supabase
    .from("cultural_signals")
    .select("id, termo, circulo, score, plataforma, raw_data, ts")
    .eq("circulo", "emergente_desconhecido")
    .order("ts", { ascending: false })
    .limit(6);

  const effectiveUnknown = unknownSignals ?? [];

  const effectiveUnknownCount = (unknownCount && unknownCount > 0) ? unknownCount : effectiveUnknown.length;

  // ── Metadados para os filtros ────────────────────────────────────────────
  const { count: total } = await supabase
    .from("cultural_signals")
    .select("*", { count: "exact", head: true });

  const effectiveTotal = (total && total > 0) ? total : effectiveSignals.length;

  const circulos = Array.from(
    new Set((effectiveSignals ?? []).map((s) => s.circulo).filter(Boolean))
  ).sort();

  const tipos = Array.from(
    new Set((effectiveSignals ?? []).map((s) => s.tipo).filter(Boolean))
  ).sort();

  // ── Estatísticas rápidas ─────────────────────────────────────────────────
  const scoreAvg =
    effectiveSignals && effectiveSignals.length > 0
      ? effectiveSignals.reduce((acc, s) => acc + (s.score ?? 0), 0) / effectiveSignals.length
      : 0;

  const volumeSpikes = (effectiveSignals ?? []).filter(
    (s) => s.raw_data?.volume_spike === true
  ).length;

  const sentimentShifts = (effectiveSignals ?? []).filter(
    (s) => s.raw_data?.sentiment_shift === true
  ).length;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* 🤖 Active Learning Interface - Sincronizado com V_Project */}
      <ConversationalPrompt />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-gray-100 pb-8">
        <div className="space-y-1">
          <h1 className="text-4xl font-black tracking-tight text-gray-900">
            Sinais & Estabilidade<span className="text-violet-600">.</span>
          </h1>
          <p className="text-gray-400 font-medium text-lg">
            Monitoramento em tempo real de sinais fracos e emergentes.
          </p>
        </div>
      </div>

      {/* 📊 KPI Cards Section - V10.8 Premium UI */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <KpiCard 
          label="Sinais exibidos"
          value={String(signals?.length ?? 0)}
          icon={<Activity size={20} />}
          color="violet"
        />
        <KpiCard 
          label="Score médio"
          value={(scoreAvg * 100).toFixed(1) + "%"}
          icon={<Zap size={20} />}
          color="amber"
        />
        <KpiCard 
          label="Volume spikes"
          value={String(volumeSpikes)}
          icon={<TrendingUp size={20} />}
          color="red"
        />
        <KpiCard 
          label="Sentiment shifts"
          value={String(sentimentShifts)}
          icon={<MessageCircle size={20} />}
          color="emerald"
        />
        <KpiCard 
          label="Sinais desconhecidos"
          value={String(effectiveUnknownCount ?? 0)}
          icon={<Sparkles size={20} />}
          color="blue"
        />
      </div>

      {/* Grid de Filtros e Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Filtros */}
        <form
          method="GET"
          className="flex flex-wrap gap-3 items-end bg-white p-4 rounded-xl border border-gray-100 shadow-sm"
        >
          <FilterSelect
            name="circulo"
            label="Círculo"
            current={params.circulo ?? "todos"}
            options={["todos", ...circulos]}
          />
          <FilterSelect
            name="tipo"
            label="Tipo"
            current={params.tipo ?? "todos"}
            options={["todos", ...tipos]}
          />
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-gray-500">Score mín.</label>
            <input
              name="minScore"
              type="number"
              step="0.01"
              min="0"
              max="1"
              defaultValue={params.minScore ?? ""}
              placeholder="0.00"
              className="border border-gray-200 rounded-lg px-3 py-2 text-sm w-24 focus:outline-none focus:ring-2 focus:ring-violet-300"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-violet-600 text-white rounded-lg text-sm hover:bg-violet-700 transition self-end"
          >
            Filtrar
          </button>
          <a
            href="/dashboard/signals"
            className="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm hover:bg-gray-200 transition self-end"
          >
            Limpar
          </a>
        </form>

        {/* Status e Avisos */}
        <div className="flex flex-col gap-4">
          {/* Aviso de novos sinais desconhecidos */}
          {effectiveUnknownCount && effectiveUnknownCount > 0 ? (
            <div className="bg-yellow-50 border border-yellow-100 p-4 rounded-xl">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-yellow-800">🆕 {effectiveUnknownCount} sinais marcados como "emergente_desconhecido"</p>
                  <p className="text-xs text-yellow-700">Acumulados para análise: realize clustering periódico para promover novos círculos.</p>
                </div>
                <div className="flex gap-2">
                  <a
                    href="/dashboard/unknowns"
                    className="px-3 py-2 bg-yellow-600 text-white rounded-lg text-sm hover:bg-yellow-700"
                  >
                    Ver fila
                  </a>
                  <a
                    href="/dashboard/unknowns/cluster"
                    className="px-3 py-2 bg-white border border-yellow-200 text-yellow-700 rounded-lg text-sm hover:bg-yellow-50"
                  >
                    Rodar clustering
                  </a>
                </div>
              </div>
            </div>
          ) : null}

          {/* Status de carregamento ou erro */}
          {error ? (
            <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-sm">
              ⚠️ Erro ao carregar sinais: {error.message}
            </div>
          ) : null}
        </div>
      </div>

      {/* Candidate cards for emergente_desconhecido */}
      {unknownSignals && unknownSignals.length > 0 && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-3">Candidatos: sinais emergentes desconhecidos</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {unknownSignals.map((u: any) => (
              <div key={u.id} className="border rounded-lg p-4 bg-white">
                <p className="text-sm text-gray-500">{u.plataforma} · {new Date(u.ts).toLocaleString()}</p>
                <h3 className="font-semibold mt-2">{u.termo}</h3>
                <p className="text-xs mt-1 text-gray-600">score: {(u.score ?? 0).toFixed(2)}</p>
                <p className="text-xs mt-2 text-gray-500 line-clamp-3">{u.raw_data?.explicacao ?? "Sem explicação"}</p>
                <div className="mt-3 flex gap-2">
                  <a
                    href={`/api/unknown/promote?id=${u.id}`}
                    className="px-3 py-1 bg-violet-600 text-white rounded-lg text-xs hover:bg-violet-700"
                  >
                    Promover
                  </a>
                  <a
                    href={`/api/unknown/dismiss?id=${u.id}`}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg text-xs hover:bg-gray-200"
                  >
                    Ignorar
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tabela */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <SignalsTable signals={effectiveSignals as any} />
      </div>

      {/* Emergente / Desconhecido */}
      <div className="bg-gradient-to-br from-indigo-50 to-white p-6 rounded-xl border border-indigo-100">
        <h3 className="text-lg font-bold text-indigo-900 mb-4 flex items-center gap-2">
          <span className="flex h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />
          Sinais Emergentes em Processamento
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {effectiveUnknown?.map((sig) => (
            <div key={sig.id} className="bg-white p-4 rounded-lg border border-indigo-50 hover:shadow-md transition cursor-pointer">
              <p className="text-sm text-gray-500">{sig.plataforma} · {new Date(sig.ts).toLocaleString()}</p>
              <h3 className="font-semibold mt-2">{sig.termo}</h3>
              <p className="text-xs mt-1 text-gray-600">score: {(sig.score ?? 0).toFixed(2)}</p>
              <p className="text-xs mt-2 text-gray-500 line-clamp-3">{sig.raw_data?.explicacao ?? "Sem explicação"}</p>
              <div className="mt-3 flex gap-2">
                <a
                  href={`/api/unknown/promote?id=${sig.id}`}
                  className="px-3 py-1 bg-violet-600 text-white rounded-lg text-xs hover:bg-violet-700"
                >
                  Promover
                </a>
                <a
                  href={`/api/unknown/dismiss?id=${sig.id}`}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg text-xs hover:bg-gray-200"
                >
                  Ignorar
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Sub-componentes server-only ──────────────────────────────────────────────

function KpiCard({
  label,
  value,
  icon,
  color,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
  color: "violet" | "amber" | "red" | "emerald" | "blue";
}) {
  const themes = {
    violet: { bg: "bg-violet-50", text: "text-violet-600", border: "border-violet-100", iconBg: "bg-white" },
    amber:  { bg: "bg-amber-50", text: "text-amber-600", border: "border-amber-100", iconBg: "bg-white" },
    red:    { bg: "bg-rose-50", text: "text-rose-600", border: "border-rose-100", iconBg: "bg-white" },
    emerald:{ bg: "bg-emerald-50", text: "text-emerald-600", border: "border-emerald-100", iconBg: "bg-white" },
    blue:   { bg: "bg-blue-50", text: "text-blue-600", border: "border-blue-100", iconBg: "bg-white" },
  };

  const theme = themes[color];

  return (
    <div className={`p-5 rounded-[24px] border ${theme.border} ${theme.bg} shadow-sm transition-all hover:shadow-md group`}>
      <div className={`w-10 h-10 ${theme.iconBg} rounded-xl flex items-center justify-center ${theme.text} mb-4 shadow-sm group-hover:scale-110 transition-transform`}>
        {icon}
      </div>
      <div className="space-y-0.5">
        <p className="text-2xl font-black text-gray-900 tracking-tighter">{value}</p>
        <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{label}</p>
      </div>
    </div>
  );
}

function SummaryCard({ label, value, icon, color }: { label: string; value: string | number; icon: string; color: string }) {
  return (
    <div className={`p-4 rounded-xl border bg-white shadow-sm flex items-center gap-4 ${color}`}>
      <div className="text-2xl">{icon}</div>
      <div>
        <p className="text-[10px] uppercase font-bold text-gray-400 tracking-wider font-mono">{label}</p>
        <p className="text-xl font-black text-gray-800 leading-none">{value}</p>
      </div>
    </div>
  );
}

function FilterSelect({
  name,
  label,
  current,
  options,
}: {
  name: string;
  label: string;
  current: string;
  options: string[];
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-gray-500">{label}</label>
      <select
        name={name}
        defaultValue={current}
        className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-300 bg-white"
      >
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt === "todos" ? `Todos os ${label.toLowerCase()}s` : opt}
          </option>
        ))}
      </select>
    </div>
  );
}
