"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const SEGMENTS = [
  "Alimentação & Bebidas", "Moda & Beleza", "Tecnologia & Apps", "Entretenimento & Mídia",
  "Saúde & Bem-estar", "Esportes & Fitness", "Varejo & E-commerce", "Automotivo",
  "Finanças & Fintech", "Educação", "Turismo & Viagem", "Casa & Decoração", "Outro",
];

const REGIONS = [
  "Brasil (Geral)", "Sudeste", "Nordeste", "Sul", "Centro-Oeste", "Norte",
  "SP", "RJ", "MG", "BA", "RS", "PR", "PE", "CE",
];

const AUDIENCES = [
  "Gen Z (16-25)", "Millennials (26-40)", "Gen X (41-55)", "Boomers (55+)", "Todos",
  "Famílias", "Jovens Urbanos", "Classe A/B", "Classe C/D", "Comunidades Periféricas",
];

const CIRCLES = [
  "🎵 Música & Ritmos", "⚽ Esportes & Torcidas", "🍖 Gastronomia Regional",
  "🎭 Entretenimento Popular", "💃 Dança & Corpo", "🙏 Espiritualidade & Fé",
  "👗 Moda & Estilo", "💻 Tecnologia & Digital", "🏠 Família & Lar",
  "🌍 Identidade Regional", "📚 Educação & Conhecimento", "💰 Economia & Trabalho",
  "🌿 Sustentabilidade", "🎨 Arte & Cultura", "❤️ Saúde & Bem-estar", "🏛️ Política & Cidadania",
];

const OBJECTIVES = [
  "Pesquisa de mercado", "Monitoramento de marca", "Detecção de tendências",
  "Análise de concorrência cultural", "Planejamento de campanha",
  "Mapeamento de riscos culturais", "Identificação de oportunidades",
];

export default function NewProjectPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Step 1: Briefing
  const [name, setName] = useState("");
  const [brand, setBrand] = useState("");
  const [keywordsText, setKeywordsText] = useState("");
  const [objective, setObjective] = useState(OBJECTIVES[0]);

  // Step 2: Configuration
  const [segment, setSegment] = useState(SEGMENTS[0]);
  const [selectedRegions, setSelectedRegions] = useState<string[]>(["Brasil (Geral)"]);
  const [selectedAudiences, setSelectedAudiences] = useState<string[]>(["Todos"]);
  const [selectedCircles, setSelectedCircles] = useState<string[]>([]);
  const [periodDays, setPeriodDays] = useState(30);

  const keywords = keywordsText
    .split(/[,\n]+/)
    .map((k) => k.trim())
    .filter(Boolean);

  function toggleItem(arr: string[], item: string, setter: (v: string[]) => void) {
    setter(arr.includes(item) ? arr.filter((x) => x !== item) : [...arr, item]);
  }

  async function handleCreate() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          brand,
          keywords,
          segment,
          objective,
          regions: selectedRegions,
          audiences: selectedAudiences,
          circles: selectedCircles,
          period_days: periodDays,
        }),
      });

      const json = await res.json();
      if (!res.ok) {
        setError(json.error ?? "Erro ao criar projeto");
        setLoading(false);
        return;
      }

      // Redirect to the project page
      router.push(`/dashboard/projects/${json.data.id}`);
    } catch (err: any) {
      setError(err.message ?? "Erro inesperado");
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">+ Novo Projeto</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Defina o briefing, configure a análise e deixe nossos 18 engines trabalharem.
        </p>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-2 mb-8">
        {[
          { n: 1, label: "Briefing" },
          { n: 2, label: "Configuração" },
          { n: 3, label: "Confirmar" },
        ].map(({ n, label }) => (
          <div key={n} className="flex items-center gap-2 flex-1">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition ${
                step >= n
                  ? "bg-violet-600 text-white"
                  : "bg-gray-200 text-gray-500"
              }`}
            >
              {step > n ? "✓" : n}
            </div>
            <span className={`text-xs font-medium ${step >= n ? "text-violet-700" : "text-gray-400"}`}>
              {label}
            </span>
            {n < 3 && <div className={`flex-1 h-0.5 ${step > n ? "bg-violet-400" : "bg-gray-200"}`} />}
          </div>
        ))}
      </div>

      {/* ═══ Step 1: Briefing ═══ */}
      {step === 1 && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-5">
          <h2 className="text-lg font-semibold text-gray-800">🎯 Briefing do Projeto</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nome do Projeto *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex: Coca-Cola Nordeste Q1 2026"
              className="w-full h-10 px-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-violet-400 focus:ring-1 focus:ring-violet-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Marca / Tópico *</label>
            <input
              type="text"
              value={brand}
              onChange={(e) => setBrand(e.target.value)}
              placeholder="Ex: Havaianas, Itaú, Nubank..."
              className="w-full h-10 px-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-violet-400 focus:ring-1 focus:ring-violet-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Keywords do Briefing * <span className="text-gray-400 font-normal">(separar por vírgula ou enter)</span>
            </label>
            <textarea
              value={keywordsText}
              onChange={(e) => setKeywordsText(e.target.value)}
              placeholder="Ex: sandálias, praia verão, streetwear brasileiro, cultura jovem..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-violet-400 focus:ring-1 focus:ring-violet-400 resize-none"
            />
            {keywords.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {keywords.map((kw, i) => (
                  <span key={i} className="text-xs bg-violet-50 text-violet-600 px-2 py-0.5 rounded-full">
                    {kw}
                  </span>
                ))}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Objetivo</label>
            <select
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              className="w-full h-10 px-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-violet-400"
            >
              {OBJECTIVES.map((o) => (
                <option key={o} value={o}>{o}</option>
              ))}
            </select>
          </div>

          <div className="flex justify-end pt-2">
            <button
              onClick={() => setStep(2)}
              disabled={!name.trim() || !brand.trim() || keywords.length === 0}
              className="px-6 py-2.5 bg-violet-600 text-white font-semibold rounded-xl text-sm hover:bg-violet-500 transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Próximo →
            </button>
          </div>
        </div>
      )}

      {/* ═══ Step 2: Configuration ═══ */}
      {step === 2 && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-5">
          <h2 className="text-lg font-semibold text-gray-800">⚙️ Configuração da Análise</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Segmento</label>
            <select
              value={segment}
              onChange={(e) => setSegment(e.target.value)}
              className="w-full h-10 px-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-violet-400"
            >
              {SEGMENTS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Regiões-alvo</label>
            <div className="flex flex-wrap gap-1.5">
              {REGIONS.map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => toggleItem(selectedRegions, r, setSelectedRegions)}
                  className={`text-xs px-3 py-1.5 rounded-full border transition ${
                    selectedRegions.includes(r)
                      ? "bg-violet-100 text-violet-700 border-violet-200"
                      : "bg-gray-50 text-gray-500 border-gray-200 hover:border-violet-200"
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Audiências-alvo</label>
            <div className="flex flex-wrap gap-1.5">
              {AUDIENCES.map((a) => (
                <button
                  key={a}
                  type="button"
                  onClick={() => toggleItem(selectedAudiences, a, setSelectedAudiences)}
                  className={`text-xs px-3 py-1.5 rounded-full border transition ${
                    selectedAudiences.includes(a)
                      ? "bg-blue-100 text-blue-700 border-blue-200"
                      : "bg-gray-50 text-gray-500 border-gray-200 hover:border-blue-200"
                  }`}
                >
                  {a}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Círculos Culturais <span className="text-gray-400 font-normal">(selecione até 16)</span>
            </label>
            <div className="grid grid-cols-2 gap-1.5">
              {CIRCLES.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => toggleItem(selectedCircles, c, setSelectedCircles)}
                  className={`text-xs px-3 py-2 rounded-lg border text-left transition ${
                    selectedCircles.includes(c)
                      ? "bg-amber-50 text-amber-700 border-amber-200"
                      : "bg-gray-50 text-gray-500 border-gray-200 hover:border-amber-200"
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Período de análise</label>
            <select
              value={periodDays}
              onChange={(e) => setPeriodDays(Number(e.target.value))}
              className="w-full h-10 px-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-violet-400"
            >
              <option value={7}>Últimos 7 dias</option>
              <option value={14}>Últimos 14 dias</option>
              <option value={30}>Últimos 30 dias</option>
              <option value={60}>Últimos 60 dias</option>
              <option value={90}>Últimos 90 dias</option>
            </select>
          </div>

          <div className="flex justify-between pt-2">
            <button
              onClick={() => setStep(1)}
              className="px-6 py-2.5 text-gray-600 font-medium rounded-xl text-sm hover:bg-gray-100 transition"
            >
              ← Voltar
            </button>
            <button
              onClick={() => setStep(3)}
              className="px-6 py-2.5 bg-violet-600 text-white font-semibold rounded-xl text-sm hover:bg-violet-500 transition"
            >
              Próximo →
            </button>
          </div>
        </div>
      )}

      {/* ═══ Step 3: Confirm ═══ */}
      {step === 3 && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-5">
          <h2 className="text-lg font-semibold text-gray-800">✅ Confirmar Projeto</h2>

          <div className="bg-gray-50 rounded-xl p-5 space-y-3 text-sm">
            <Row label="Nome" value={name} />
            <Row label="Marca" value={brand} />
            <Row label="Keywords" value={keywords.join(", ")} />
            <Row label="Objetivo" value={objective} />
            <Row label="Segmento" value={segment} />
            <Row label="Regiões" value={selectedRegions.join(", ")} />
            <Row label="Audiências" value={selectedAudiences.join(", ")} />
            <Row label="Círculos" value={selectedCircles.length > 0 ? selectedCircles.join(", ") : "Todos (16)"} />
            <Row label="Período" value={`${periodDays} dias`} />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-100 text-red-700 text-sm rounded-lg p-3">
              {error}
            </div>
          )}

          <div className="flex justify-between pt-2">
            <button
              onClick={() => setStep(2)}
              className="px-6 py-2.5 text-gray-600 font-medium rounded-xl text-sm hover:bg-gray-100 transition"
            >
              ← Voltar
            </button>
            <button
              onClick={handleCreate}
              disabled={loading}
              className="px-8 py-2.5 bg-violet-600 text-white font-semibold rounded-xl text-sm hover:bg-violet-500 transition disabled:opacity-60"
            >
              {loading ? "Criando..." : "🚀 Criar Projeto"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex">
      <span className="w-24 text-gray-500 shrink-0">{label}</span>
      <span className="font-medium text-gray-800">{value}</span>
    </div>
  );
}
