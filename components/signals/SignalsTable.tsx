"use client";

import { useState } from "react";
import type { CulturalSignal } from "@/app/dashboard/signals/page";
import { VeracityLineage } from "./VeracityLineage";

// ── helpers ──────────────────────────────────────────────────────────────────

function scoreBar(score: number) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 70 ? "bg-green-500" : pct >= 45 ? "bg-amber-400" : "bg-violet-400";
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono text-gray-600">{(pct / 100).toFixed(3)}</span>
    </div>
  );
}

function PlatformBadge({ plataforma }: { plataforma: string }) {
  const MAP: Record<string, { bg: string; emoji: string }> = {
    YouTube:   { bg: "bg-red-100 text-red-700",     emoji: "▶️" },
    Reddit:    { bg: "bg-orange-100 text-orange-700",emoji: "🤖" },
    Spotify:   { bg: "bg-green-100 text-green-700",  emoji: "🎵" },
    Instagram: { bg: "bg-pink-100 text-pink-700",    emoji: "📸" },
    Meetup:    { bg: "bg-blue-100 text-blue-700",    emoji: "📅" },
    IBGE:      { bg: "bg-teal-100 text-teal-700",    emoji: "📊" },
    NewsAPI:   { bg: "bg-gray-100 text-gray-700",    emoji: "📰" },
  };
  const style = MAP[plataforma] ?? { bg: "bg-gray-100 text-gray-600", emoji: "🌐" };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${style.bg}`}>
      {style.emoji} {plataforma}
    </span>
  );
}

function CirculoBadge({ circulo }: { circulo: string }) {
  const MAP: Record<string, string> = {
    música:           "bg-violet-100 text-violet-700",
    moda:             "bg-pink-100 text-pink-700",
    tecnologia:       "bg-blue-100 text-blue-700",
    gastronomia:      "bg-orange-100 text-orange-700",
    saúde:            "bg-green-100 text-green-700",
    comportamento:    "bg-amber-100 text-amber-700",
    política:         "bg-red-100 text-red-700",
    sustentabilidade: "bg-teal-100 text-teal-700",
    esporte:          "bg-cyan-100 text-cyan-700",
    games:            "bg-indigo-100 text-indigo-700",
    cultura_geral:    "bg-gray-100 text-gray-600",
  };
  const cls = MAP[circulo] ?? "bg-gray-100 text-gray-600";
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${cls}`}>
      {circulo}
    </span>
  );
}

function TypeBadge({ tipo, rareness }: { tipo: string; rareness?: number }) {
  const MAP: Record<string, string> = {
    sinal_fraco:    "bg-yellow-50 text-yellow-700 border border-yellow-200",
    sinal_viral:    "bg-red-50 text-red-700 border border-red-300",
    sinal_emergente:"bg-green-50 text-green-700 border border-green-300",
    sinal_cultural: "bg-gray-50 text-gray-600 border border-gray-200",
    Teste:          "bg-slate-50 text-slate-500 border border-slate-200",
    Simulacao:      "bg-slate-50 text-slate-500 border border-slate-200",
  };
  const cls = MAP[tipo] ?? "bg-gray-50 text-gray-500 border border-gray-200";
  
  // Badge extra de Raridade baseada no novo score V9.3
  const isRare = rareness && rareness >= 0.75;
  
  return (
    <div className="flex flex-col gap-1 items-start">
      <span className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full font-bold ${cls}`}>
        {tipo.replace("sinal_", "")}
      </span>
      {isRare && (
        <span className="text-[9px] bg-purple-600 text-white px-1.5 py-0.5 rounded-sm font-bold animate-pulse">
          ✨ RARO / UNDERGROUND
        </span>
      )}
    </div>
  );
}

function BoolIndicator({ value, label }: { value?: boolean; label: string }) {
  // ... existing code ...
  return value ? (
    <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
      ✓ {label}
    </span>
  ) : null;
}

function formatTs(ts: string) {
  try {
    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(new Date(ts));
  } catch {
    return ts;
  }
}

// ── Linha expandível ─────────────────────────────────────────────────────────

function SignalRow({ signal }: { signal: CulturalSignal }) {
  const [open, setOpen] = useState(false);
  const raw = signal.raw_data ?? {};
  
  // Detecção de Veracidade Biográfica Dinâmica (V9.9)
  const isVerified = signal.is_verified || raw.is_verified;
  const reliability = signal.reliability || raw.reliability;

  return (
    <>
      <tr
        onClick={() => setOpen((o) => !o)}
        className="hover:bg-violet-50/40 cursor-pointer transition-colors border-b border-gray-100"
      >
        <td className="px-4 py-3 text-xs text-gray-400 font-mono">{signal.id}</td>
        <td className="px-4 py-3">
          <div className="flex flex-col">
            <span className="font-semibold text-gray-800 text-sm">{signal.termo}</span>
            {isVerified && (
              <span className="text-[9px] text-green-600 font-black flex items-center gap-0.5 animate-pulse">
                🛡️ VERIFICADO (BIOGRÁFICO)
              </span>
            )}
          </div>
        </td>
        <td className="px-4 py-3"><CirculoBadge circulo={signal.circulo} /></td>
        <td className="px-4 py-3"><TypeBadge tipo={signal.tipo} rareness={raw.rareness_score} /></td>
        <td className="px-4 py-3"><PlatformBadge plataforma={signal.plataforma} /></td>
        <td className="px-4 py-3">{momentumGauge(raw.momentum ?? 0, raw.momentum_velocity ?? 0)}</td>
        <td className="px-4 py-3">
          <div className="flex flex-col gap-1">
            <div className="flex gap-1 flex-wrap">
              <BoolIndicator value={raw.volume_spike}    label="spike" />
              <BoolIndicator value={raw.sentiment_shift} label="sentiment" />
              <BoolIndicator value={raw.visual_proof}    label="visual" />
            </div>
            {reliability === "ALTA" && (
              <span className="text-[10px] font-bold text-green-600 bg-green-50 px-1 rounded">
                ✅ CONFIRMADO
              </span>
            )}
          </div>
        </td>
        <td className="px-4 py-3 text-xs text-gray-400">{formatTs(signal.ts)}</td>
        <td className="px-4 py-3 text-gray-400 text-xs">{open ? "▲" : "▼"}</td>
      </tr>

      {open && (
        <tr className="bg-gray-50 border-b border-gray-200">
          <td colSpan={9} className="px-6 py-4">
            
            {/* 🆕 V9.9: Veracity Lineage & Evidence UI (RESTAURADO E AMPLIADO) */}
            <VeracityLineage signal={{
              reliability: reliability,
              accuracy_score: signal.accuracy_score || raw.accuracy_score,
              is_verified: isVerified,
              visual_proof: signal.visual_proof || raw.visual_proof,
              cross_verified: signal.cross_verified || raw.cross_verified,
              plataforma: signal.plataforma,
              thumbnail: signal.thumbnail || raw.thumbnail,
              image_url: signal.image_url || raw.image_url,
              url: signal.url || raw.url,
              calculation_details: raw.calculation_details
            }} />

            {/* 🎯 Campaign Match v9.6 (Preditivo) */}
            {raw.campaign_fit != null && (
              <div className="mb-6 p-4 bg-gradient-to-r from-violet-600 to-indigo-700 rounded-xl text-white shadow-xl relative overflow-hidden">
                <div className="relative z-10">
                  <div className="flex justify-between items-end mb-2">
                    <div>
                      <h4 className="text-[10px] font-black uppercase tracking-widest text-violet-100 opacity-80">Campaign Fit Score</h4>
                      <p className="text-2xl font-black">{(raw.campaign_fit * 100).toFixed(0)}% <span className="text-sm font-medium opacity-70">Sinergia Cultural</span></p>
                    </div>
                    <div className="text-right">
                      <p className="text-[9px] font-bold opacity-60">RECOMENDAÇÃO</p>
                      <p className="text-xs font-bold">{raw.campaign_fit > 0.8 ? "🚀 EXECUTAR AGRESSIVAMENTE" : "⚠️ AJUSTAR TOM DE VOZ"}</p>
                    </div>
                  </div>
                  <div className="w-full h-1.5 bg-white/20 rounded-full overflow-hidden">
                    <div className="h-full bg-green-400 shadow-[0_0_12px_rgba(74,222,128,0.8)]" style={{ width: `${raw.campaign_fit * 100}%` }} />
                  </div>
                </div>
                {/* Efeito decorativo */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -mr-16 -mt-16 blur-3xl pointer-events-none" />
              </div>
            )}

            {/* Visual Evidence V9.5/9.6 */}
            {raw.evidence && raw.evidence.length > 0 && (
              <div className="mb-6">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
                    📸 Prova Visual de Campo (Multimodal)
                  </h4>
                  {isVerified ? (
                    <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded-full text-[10px] font-bold border border-green-200 shadow-sm animate-pulse">
                      ✅ VERIFICADO POR ML (V9.6)
                    </span>
                  ) : (
                    <span className="bg-amber-50 text-amber-600 px-2 py-0.5 rounded-full text-[10px] font-bold border border-amber-100">
                      ⚖️ EM ANÁLISE DE AUDITORIA
                    </span>
                  )}
                </div>
                <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-hide">
                  {raw.evidence.map((ev: any, idx: number) => (
                    <a 
                      key={idx} 
                      href={ev.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex-shrink-0 w-48 group"
                    >
                      <div className="relative aspect-video rounded-lg overflow-hidden border border-gray-200 bg-gray-100">
                        <img 
                          src={ev.thumbnail} 
                          alt={ev.title} 
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                        />
                        <div className="absolute inset-0 bg-black/20 group-hover:bg-black/0 transition-colors" />
                        <div className="absolute bottom-1 right-1 bg-black/60 text-white text-[10px] px-1 rounded">
                          {ev.platform}
                        </div>
                      </div>
                      <p className="mt-1.5 text-[11px] font-medium text-gray-700 line-clamp-2 leading-snug group-hover:text-violet-600">
                        {ev.title}
                      </p>
                      <p className="text-[10px] text-gray-400 mt-0.5">
                        👤 {ev.channel}
                      </p>
                    </a>
                  ))}
                </div>
              </div>
            )}

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm mt-4 border-t border-gray-100 pt-4">
              <Metric label="Momentum"  value={raw.momentum?.toFixed(2) ?? "—"} />
              <Metric label="Volume"    value={String(raw.volume ?? "—")} />
              <Metric label="Autenticidade (AI)" value={raw.authenticity_score != null ? `${(raw.authenticity_score * 100).toFixed(0)}%` : "—"} />
              <Metric label="Região"    value={signal.regiao ?? "—"} />
            </div>
            {raw.explicacao && (
              <div className="mt-4 p-3 bg-violet-50 rounded-lg text-xs border border-violet-100 italic text-violet-900 leading-relaxed shadow-sm">
                <span className="font-bold block mb-1 uppercase text-[9px] text-violet-400 tracking-wider">Por que este sinal é relevante?</span>
                {raw.explicacao}
              </div>
            )}

            {/* V9.9: Narrativa Cultural e Estratégia via IA Local (Llama-3) */}
            {(raw.narrativa_cultural || raw.recomendacao_acao) && (
              <div className="mt-4 space-y-4">
                {raw.narrativa_cultural && (
                  <div className="p-4 bg-emerald-50/30 rounded-xl border border-emerald-100/50 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-2 opacity-20 group-hover:opacity-100 transition-opacity">
                      <span className="text-[10px] bg-emerald-600 text-white px-2 py-0.5 rounded-full font-bold">IA LOCAL</span>
                    </div>
                    <span className="font-bold mb-2 uppercase text-[10px] text-emerald-600 tracking-widest flex items-center gap-2">
                      <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                      Alma Cultural (Narrativa SLM)
                    </span>
                    <p className="text-sm text-emerald-950 leading-relaxed font-medium">
                      {raw.narrativa_cultural}
                    </p>
                  </div>
                )}

                {raw.recomendacao_acao && (
                  <div className="p-4 bg-blue-50/30 rounded-xl border border-blue-100/50 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-2 opacity-20 group-hover:opacity-100 transition-opacity">
                      <span className="text-[10px] bg-blue-600 text-white px-2 py-0.5 rounded-full font-bold">ESTRATÉGIA</span>
                    </div>
                    <span className="font-bold mb-2 uppercase text-[10px] text-blue-600 tracking-widest flex items-center gap-2">
                       🎯 Consultoria de Negócio (Llama-3)
                    </span>
                    <p className="text-sm text-blue-950 leading-relaxed italic whitespace-pre-wrap">
                      {raw.recomendacao_acao}
                    </p>
                  </div>
                )}
              </div>
            )}
          </td>
        </tr>
      )}
    </>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-gray-400">{label}</p>
      <p className="font-medium text-gray-800">{value}</p>
    </div>
  );
}

function momentumGauge(momentum: number, velocity: number = 0) {
  const pct = Math.round(momentum * 100);
  const isAccelerating = velocity > 0.5;
  const color =
    pct >= 70 ? "bg-red-500" : pct >= 45 ? "bg-orange-400" : "bg-blue-400";
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2">
        <div className="w-20 h-2 bg-gray-100 rounded-full overflow-hidden shrink-0">
          <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${pct}%` }} />
        </div>
        <span className="text-[10px] font-bold text-gray-800">{pct}%</span>
      </div>
      {isAccelerating && (
        <span className="text-[9px] text-red-500 font-black animate-pulse flex items-center gap-0.5">
          🚀 ACELERAÇÃO AGRESSIVA
        </span>
      )}
    </div>
  );
}

function ContextHeatmap({ tags }: { tags?: string[] }) {
  if (!tags || tags.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-1 mt-2">
      {tags.map((tag, i) => (
        <span key={i} className="text-[9px] px-1.5 py-0.5 bg-violet-600/10 text-violet-700 rounded border border-violet-200/50 font-medium">
          #{tag}
        </span>
      ))}
    </div>
  );
}

function TensionQuadrant({ tension, sentiment }: { tension: number, sentiment: number }) {
  // tension [0,1], sentiment [-1,1]
  const isRisk = tension > 0.7 && sentiment < 0;
  return (
    <div className="mt-4 p-3 bg-white border border-gray-100 rounded-lg">
      <div className="flex justify-between items-center mb-2">
        <span className="text-[9px] font-bold text-gray-400 uppercase tracking-widest">Matriz de Tensão & Risco</span>
        {isRisk && (
          <span className="text-[9px] bg-red-600 text-white px-1.5 py-0.5 rounded font-black animate-bounce shadow-lg">
            ⚠️ RISCO BRAND SAFETY
          </span>
        )}
      </div>
      <div className="relative h-20 w-full bg-gray-50 border border-dashed border-gray-200 rounded flex items-center justify-center overflow-hidden">
        {/* Cruz de Quadrantes */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-full w-[1px] bg-gray-200" />
          <div className="w-full h-[1px] bg-gray-200" />
        </div>
        {/* Ponto do Sinal */}
        <div 
          className={`absolute w-3 h-3 rounded-full border-2 border-white shadow-xl transition-all duration-700 ${isRisk ? "bg-red-500 scale-125" : "bg-violet-600 shadow-violet-500/50"}`}
          style={{ 
            left: `${(sentiment + 1) * 50}%`, 
            bottom: `${(tension) * 100}%`,
            transform: "translate(-50%, 50%)" 
          }}
        />
        <span className="absolute top-2 left-2 text-[8px] text-gray-300">CALMO / NEG</span>
        <span className="absolute top-2 right-2 text-[8px] text-gray-300">CALMO / POS</span>
        <span className="absolute bottom-2 left-2 text-[8px] text-gray-300">TENSO / NEG</span>
        <span className="absolute bottom-2 right-2 text-[8px] text-gray-300">TENSO / POS</span>
      </div>
    </div>
  );
}

// ── Componente principal ─────────────────────────────────────────────────────

export default function SignalsTable({ signals }: { signals: CulturalSignal[] }) {
  const [sortKey, setSortKey] = useState<"score" | "ts" | "termo">("ts");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  function toggleSort(key: typeof sortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  const sorted = [...signals].sort((a, b) => {
    let va: string | number = a[sortKey] ?? "";
    let vb: string | number = b[sortKey] ?? "";
    if (typeof va === "string" && typeof vb === "string") {
      return sortDir === "asc" ? va.localeCompare(vb) : vb.localeCompare(va);
    }
    return sortDir === "asc"
      ? (va as number) - (vb as number)
      : (vb as number) - (va as number);
  });

  function SortBtn({ col }: { col: typeof sortKey }) {
    return (
      <button
        onClick={() => toggleSort(col)}
        className="ml-1 text-gray-400 hover:text-gray-700"
      >
        {sortKey === col ? (sortDir === "asc" ? "↑" : "↓") : "↕"}
      </button>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <p className="text-sm font-medium text-gray-700">
          {signals.length} sinais · clique numa linha para expandir detalhes
        </p>
        <p className="text-xs text-gray-400">Dados reais · Supabase</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wider">
            <tr>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">
                Termo <SortBtn col="termo" />
              </th>
              <th className="px-4 py-3">Círculo</th>
              <th className="px-4 py-3">Tipo</th>
              <th className="px-4 py-3">Plataforma</th>
              <th className="px-4 py-3">
                Score <SortBtn col="score" />
              </th>
              <th className="px-4 py-3">Sinais</th>
              <th className="px-4 py-3">
                Data <SortBtn col="ts" />
              </th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {sorted.map((s) => (
              <SignalRow key={s.id} signal={s} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
