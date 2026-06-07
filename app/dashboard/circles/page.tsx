import { createClient } from "@/lib/supabase/server";
import CirclesSunburst from "@/components/charts/CirclesSunburst";
import CircleCards from "@/components/circles/CircleCards";

export const revalidate = 60;

// ── Normalização de nomes de círculos ────────────────────────────────────────

const CIRCLE_NORMALIZE: Record<string, string> = {
  música:              "Música",
  musica:              "Música",
  musica_ritmo:        "Música",
  "MUSICA":            "Música",
  tecnologia:          "Tecnologia",
  "TECNOLOGIA":        "Tecnologia",
  gastronomia:         "Gastronomia",
  gastronomia_sabor:   "Gastronomia",
  "GASTRONOMIA":       "Gastronomia",
  moda:                "Moda & Estilo",
  "MODA":              "Moda & Estilo",
  comportamento:       "Comportamento",
  "COMPORTAMENTO":     "Comportamento",
  saúde:               "Saúde & Bem-estar",
  saude:               "Saúde & Bem-estar",
  "SAUDE":             "Saúde & Bem-estar",
  política:            "Política",
  politica:            "Política",
  "POLITICA":          "Política",
  sustentabilidade:    "Sustentabilidade",
  "SUSTENTABILIDADE":  "Sustentabilidade",
  esporte:             "Esporte",
  "ESPORTE":           "Esporte",
  arte:                "Arte & Cinema",
  "ARTE":              "Arte & Cinema",
  educacao:            "Educação",
  "EDUCACAO":          "Educação",
  religiao:            "Espiritualidade",
  "RELIGIAO":          "Espiritualidade",
  turismo:             "Turismo",
  "TURISMO":           "Turismo",
  juventude:           "Juventude",
  "JUVENTUDE":         "Juventude",
  familia:             "Família & Lar",
  "FAMILIA":           "Família & Lar",
  economia:            "Economia",
  "ECONOMIA":          "Economia",
};

const CIRCLE_CATEGORIA: Record<string, string> = {
  "Música":            "Entretenimento",
  "Tecnologia":        "Comportamento",
  "Gastronomia":       "Consumo",
  "Moda & Estilo":     "Consumo",
  "Comportamento":     "Comportamento",
  "Saúde & Bem-estar": "Comportamento",
  "Política":          "Identidade",
  "Sustentabilidade":  "Identidade",
  "Esporte":           "Entretenimento",
  "Arte & Cinema":     "Entretenimento",
  "Educação":          "Identidade",
  "Espiritualidade":   "Espiritualidade",
  "Turismo":           "Consumo",
  "Juventude":         "Comportamento",
  "Família & Lar":     "Comportamento",
  "Economia":          "Identidade",
};

const CIRCLE_ICON: Record<string, string> = {
  "Música":            "🎵",
  "Tecnologia":        "💻",
  "Gastronomia":       "🍽️",
  "Moda & Estilo":     "👗",
  "Comportamento":     "🧠",
  "Saúde & Bem-estar": "💚",
  "Política":          "🏛️",
  "Sustentabilidade":  "♻️",
  "Esporte":           "⚽",
  "Arte & Cinema":     "🎨",
  "Educação":          "📚",
  "Espiritualidade":   "🙏",
  "Turismo":           "✈️",
  "Juventude":         "⚡",
  "Família & Lar":     "🏠",
  "Economia":          "📊",
};

function normalizeCircle(raw: string): string {
  return CIRCLE_NORMALIZE[raw] ?? CIRCLE_NORMALIZE[raw.toLowerCase()] ?? raw;
}

// ── Tipos ────────────────────────────────────────────────────────────────────

interface CircleAgg {
  name:       string;
  categoria:  string;
  icon:       string;
  totalSignals: number;
  avgScore:   number;
  maxScore:   number;
  platforms:  string[];
  topTermos:  Array<{ termo: string; score: number; count: number }>;
}

// ── Page ─────────────────────────────────────────────────────────────────────

export default async function CirclesPage() {
  const supabase = createClient();

  const { data: signals, error } = await supabase
    .from("cultural_signals")
    .select("id, circulo, termo, score, plataforma, raw_data, ts")
    .not("plataforma", "eq", "internal")
    .order("ts", { ascending: false })
    .limit(500);

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-sm">
          ⚠️ Erro ao carregar dados: {error.message}
        </div>
      </div>
    );
  }

  const rows = signals ?? [];

  // ── Agregar por círculo ────────────────────────────────────────────────
  const circleMap = new Map<string, {
    scores: number[];
    termoMap: Map<string, { scores: number[]; count: number }>;
    platforms: Set<string>;
  }>();

  for (const row of rows) {
    const name = normalizeCircle(row.circulo ?? "Outros");
    if (!circleMap.has(name)) {
      circleMap.set(name, { scores: [], termoMap: new Map(), platforms: new Set() });
    }
    const entry = circleMap.get(name)!;
    entry.scores.push(row.score ?? 0);
    entry.platforms.add(row.plataforma);

    const termo = row.termo ?? "?";
    if (!entry.termoMap.has(termo)) {
      entry.termoMap.set(termo, { scores: [], count: 0 });
    }
    const t = entry.termoMap.get(termo)!;
    t.scores.push(row.score ?? 0);
    t.count += 1;
  }

  const circles: CircleAgg[] = Array.from(circleMap.entries())
    .map(([name, data]) => {
      const avgScore = data.scores.reduce((a, b) => a + b, 0) / data.scores.length;
      const maxScore = Math.max(...data.scores);
      const topTermos = Array.from(data.termoMap.entries())
        .map(([termo, td]) => ({
          termo,
          score: td.scores.reduce((a, b) => a + b, 0) / td.scores.length,
          count: td.count,
        }))
        .sort((a, b) => b.score - a.score)
        .slice(0, 5);

      return {
        name,
        categoria: CIRCLE_CATEGORIA[name] ?? "Outros",
        icon: CIRCLE_ICON[name] ?? "🔵",
        totalSignals: data.scores.length,
        avgScore,
        maxScore,
        platforms: Array.from(data.platforms),
        topTermos,
      };
    })
    .sort((a, b) => b.avgScore - a.avgScore);

  // ── Dados para o Sunburst ──────────────────────────────────────────────
  const sunburstData = circles.map((c) => ({
    circulo:   c.name,
    categoria: c.categoria,
    score:     Math.round(c.avgScore * 100),
    termos:    c.topTermos.map((t) => ({
      termo: t.termo,
      score: Math.round(t.score * 100),
    })),
  }));

  // ── KPIs ───────────────────────────────────────────────────────────────
  const totalSignals = rows.length;
  const totalCircles = circles.length;
  const avgGlobal = rows.reduce((a, r) => a + (r.score ?? 0), 0) / (rows.length || 1);
  const totalPlatforms = new Set(rows.map((r) => r.plataforma)).size;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            🔵 Círculos Culturais
          </h1>
          <p className="text-gray-500 text-sm mt-0.5">
            Mapeamento dos 16 círculos culturais brasileiros · {totalSignals} sinais analisados
          </p>
        </div>
        <a
          href="/dashboard/circles"
          className="text-xs bg-violet-600 text-white px-4 py-2 rounded-lg hover:bg-violet-700 transition"
        >
          ↻ Atualizar
        </a>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <KpiCard label="Círculos ativos" value={String(totalCircles)} icon="🔵" color="violet" />
        <KpiCard label="Total sinais" value={String(totalSignals)} icon="📡" color="amber" />
        <KpiCard label="Score médio" value={`${(avgGlobal * 100).toFixed(1)}%`} icon="⚡" color="green" />
        <KpiCard label="Plataformas" value={String(totalPlatforms)} icon="🌐" color="blue" />
      </div>

      {/* Sunburst */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CirclesSunburst signals={sunburstData} height={420} />

        {/* Top Circles Ranking */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">
            🏆 Ranking dos Círculos
          </h3>
          <div className="space-y-3">
            {circles.slice(0, 10).map((c, i) => (
              <div key={c.name} className="flex items-center gap-3">
                <span className="text-lg w-8 text-center font-bold text-gray-300">
                  {i + 1}
                </span>
                <span className="text-xl">{c.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-800 truncate">
                      {c.name}
                    </span>
                    <span className="text-xs text-gray-400 ml-2">
                      {c.totalSignals} sinais
                    </span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-violet-500 rounded-full transition-all"
                        style={{ width: `${Math.round(c.avgScore * 100)}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono text-gray-500 w-12 text-right">
                      {(c.avgScore * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Circle Cards */}
      <CircleCards circles={circles as any} />
    </div>
  );
}

// ── Sub-components ───────────────────────────────────────────────────────────

function KpiCard({
  label,
  value,
  icon,
  color,
}: {
  label: string;
  value: string;
  icon: string;
  color: "violet" | "amber" | "green" | "blue";
}) {
  const colors = {
    violet: "bg-violet-50 text-violet-700 border-violet-100",
    amber:  "bg-amber-50 text-amber-700 border-amber-100",
    green:  "bg-green-50 text-green-700 border-green-100",
    blue:   "bg-blue-50 text-blue-700 border-blue-100",
  };
  return (
    <div className={`rounded-xl border p-4 ${colors[color]}`}>
      <p className="text-2xl">{icon}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      <p className="text-xs opacity-70 mt-0.5">{label}</p>
    </div>
  );
}
