"use client";
import React, { useState } from 'react';
import { Info, Target, TrendingUp, AlertCircle, Zap } from 'lucide-react';

interface NatureType {
  id: string;
  label: string;
  color: string;
  description: string;
  lightColor: string;
}

const NATURE_TYPES: NatureType[] = [
    { id: 'organico', label: 'Sinal Orgânico', color: '#10b981', lightColor: '#ecfdf5', description: 'Crescimento natural e engajamento genuíno sem impulsão.' },
    { id: 'setorial', label: 'Sinal Setorial', color: '#3b82f6', lightColor: '#eff6ff', description: 'Tendências e movimentos específicos do setor de atuação.' },
    { id: 'comercial', label: 'Sinal Comercial', color: '#a855f7', lightColor: '#f5f3ff', description: 'Intenção de compra, promoções e conversão direta.' },
    { id: 'sintetico', label: 'Sinal Sintético (BOT)', color: '#ef4444', lightColor: '#fef2f2', description: 'Atividade automatizada ou coordenada por bots detectada.' },
    { id: 'noticioso', label: 'Sinal Institucional/Noticioso', color: '#0ea5e9', lightColor: '#f0f9ff', description: 'Cobertura de PR, notícias e comunicados oficiais.' },
    { id: 'transicional', label: 'Sinal Transicional', color: '#f59e0b', lightColor: '#fffbeb', description: 'Sinais migrando de nichos para o mainstream.' },
    { id: 'influencia', label: 'Sinal de Influência', color: '#ec4899', lightColor: '#fdf2f8', description: 'Movimentado por creators e formadores de opinião.' },
    { id: 'emergente', label: 'Sinal Emergente', color: '#6366f1', lightColor: '#e0e7ff', description: 'Novos comportamentos detectados em fase inicial.' },
];

const SIGNAL_MOCK_DATA: Record<string, { nature: string, name: string, score: number, affinity: number, harmonicFreq: number, tension: string }> = {
  '1': { nature: 'emergente', name: 'Brasilidade', score: 88, affinity: 92, harmonicFreq: 79, tension: 'Média' },
  '2': { nature: 'influencia', name: 'Sertanejo Pop', score: 74, affinity: 85, harmonicFreq: 68, tension: 'Alta' },
  '3': { nature: 'sintetico', name: 'IA Generativa', score: 42, affinity: 35, harmonicFreq: 42, tension: 'Média' },
  '4': { nature: 'organico', name: 'Ancestralidade', score: 91, affinity: 96, harmonicFreq: 88, tension: 'Baixa' },
  '5': { nature: 'comercial', name: 'Tecnologia', score: 65, affinity: 72, harmonicFreq: 55, tension: 'Alta' },
  '6': { nature: 'transicional', name: 'Sustentabilidade', score: 78, affinity: 81, harmonicFreq: 72, tension: 'Média' },
  '7': { nature: 'setorial', name: 'Economia Circular', score: 58, affinity: 64, harmonicFreq: 48, tension: 'Baixa' },
  'default': { nature: 'setorial', name: 'Sinal Captado', score: 50, affinity: 50, harmonicFreq: 50, tension: 'Média' }
};

interface SignalNatureProps {
    selectedSignalId?: string | null;
    brandPosition?: string;
    brandScore?: number;
}

export default function SignalNatureClassification({ 
    selectedSignalId = null, 
    brandPosition = 'organico',
    brandScore = 82
}: SignalNatureProps) {
    const selectedData = selectedSignalId ? (SIGNAL_MOCK_DATA[selectedSignalId] || SIGNAL_MOCK_DATA['default']) : null;
    const selectedSignalNature = selectedData?.nature || null;
    
    const activeBrandNature = NATURE_TYPES.find(n => n.id === brandPosition) || NATURE_TYPES[0];
    const activeSignalNature = NATURE_TYPES.find(n => n.id === selectedSignalNature);
    const currentSignalName = selectedData?.name || "Sinal Captado";

  return (
    <div className="bg-white rounded-[40px] border border-gray-100 shadow-sm p-8 flex flex-col h-full min-h-[600px] transition-all duration-500 hover:border-violet-100">
      {/* Header Premium baseada no anexo */}
      <div className="flex justify-between items-start">
        <div className="space-y-1">
          <h2 className="text-2xl font-black text-[#1e1b4b] tracking-tight">Diagnóstico de Natureza Cultural</h2>
          <p className="text-sm text-gray-400 font-medium">
            {selectedSignalId 
              ? `Análise Comparativa: Marca vs. ${currentSignalName}` 
              : "Posicionamento Estratégico da Marca / Tópico"}
          </p>
        </div>
        <div className="bg-violet-50 px-4 py-2 rounded-2xl border border-violet-100 flex items-center gap-2">
          <TrendingUp size={14} className="text-violet-600" />
          <span className="text-[10px] font-black text-violet-700 uppercase tracking-widest">Sinais Captados: 12.8k</span>
        </div>
      </div>

      {/* Dynamic Info Banner - REFINADO V10.7 */}
      <div className={`rounded-3xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xl overflow-hidden relative group transition-all duration-500 ${selectedSignalId ? 'bg-indigo-950' : 'bg-gray-900'}`}>
        <div className="flex items-center gap-4 relative z-10">
          <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 shadow-lg ${selectedSignalId ? 'bg-violet-500' : 'bg-emerald-500'}`}>
            {selectedSignalId ? <Zap size={22} className="text-white" /> : <Target size={22} className="text-white" />}
          </div>
          <div>
            <p className="text-[10px] font-black text-indigo-300/60 uppercase tracking-widest leading-none mb-2">
              {selectedSignalId ? "Diferencial de Natureza e Veracidade" : "Status de Posicionamento"}
            </p>
            <div className="text-sm font-bold text-white leading-relaxed">
              {selectedSignalId ? (
                <>
                  O sinal <span className="text-violet-400 font-black">{currentSignalName}</span> apresenta natureza 
                  <span className="bg-violet-400/20 px-2 py-0.5 rounded-md mx-1 border border-violet-400/30 text-violet-300">{activeSignalNature?.label}</span>, 
                  o que indica uma <span className="text-gray-300">{activeSignalNature?.description.toLowerCase()}</span>
                </>
              ) : (
                <>Sua marca está consolidada como <span className="text-emerald-400 font-black">{activeBrandNature.label}</span>, garantindo ressonância em canais de {activeBrandNature.description.toLowerCase()}</>
              )}
            </div>
          </div>
        </div>

        {/* % Comparison Badges */}
        <div className="flex items-center gap-3 relative z-10 shrink-0">
          <div className="flex flex-col items-center px-4 py-2 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-sm">
            <span className="text-[9px] font-black text-emerald-400 uppercase tracking-tighter">Marca Atual</span>
            <span className="text-xl font-black text-white">{brandScore}%</span>
          </div>
          {selectedSignalId && (
            <>
              <div className="w-px h-8 bg-white/10" />
              <div className="flex flex-col items-center px-4 py-2 bg-violet-600/20 border border-violet-500/30 rounded-2xl backdrop-blur-sm">
                <span className="text-[9px] font-black text-violet-400 uppercase tracking-tighter">Sinal Captado</span>
                <span className="text-xl font-black text-white">{selectedData?.score}%</span>
              </div>
            </>
          )}
        </div>
      </div>      {/* Régua de Natureza */}
      <div className="space-y-12 py-4">
        <div className="flex items-center justify-between px-2">
          <h3 className="text-[11px] font-black text-gray-400 uppercase tracking-[0.2em]">
            Régua de Distribuição de Natureza
          </h3>
          <div className="bg-emerald-50 px-4 py-2 rounded-2xl flex items-center gap-2 border border-emerald-100">
            <span className="text-[10px] font-black text-emerald-600 uppercase tracking-tight">Status:</span>
            <span className="text-xs font-black text-emerald-700">Alta Veracidade</span>
          </div>
        </div>

        {/* The Timeline/Scale Component */}
        <div className="relative h-24 w-full flex rounded-[24px] overflow-visible border border-gray-100 shadow-inner bg-gray-50 mb-12">
          {NATURE_TYPES.map((nature) => (
            <div 
              key={nature.id}
              className="h-full flex-1 relative transition-colors duration-500"
              style={{ backgroundColor: nature.lightColor }}
            >
              <div className="absolute right-0 top-1/4 bottom-1/4 w-[1px] bg-black/5" />

              {/* BRAND MARKER (Sempre Visível) */}
              {nature.id === brandPosition && (
                <div className="absolute inset-0 flex items-center justify-center -translate-y-4">
                  <div className="relative z-20">
                    <div className="w-10 h-10 rounded-full bg-white shadow-2xl border-4 flex items-center justify-center border-emerald-500 ring-4 ring-emerald-500/10">
                      <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />
                    </div>
                    <div className="absolute -top-12 left-1/2 -translate-x-1/2 px-4 py-1.5 bg-emerald-500 rounded-full shadow-lg shadow-emerald-200/50 flex flex-col items-center">
                      <span className="text-[10px] font-black text-white uppercase leading-none">Minha Marca</span>
                      <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-l-transparent border-r-4 border-r-transparent border-t-[8px] border-t-emerald-500" />
                    </div>
                  </div>
                </div>
              )}

              {/* SIGNAL MARKER (Aparece somente quando selecionado) */}
              {selectedSignalId && nature.id === selectedSignalNature && (
                <div className="absolute inset-0 flex items-center justify-center translate-y-4 animate-in zoom-in-0 duration-500">
                  <div className="relative z-30">
                    <div className="w-10 h-10 rounded-full bg-white shadow-2xl border-4 flex items-center justify-center border-violet-500 ring-4 ring-violet-500/10">
                      <div className="w-3 h-3 rounded-full bg-violet-600 shadow-[0_0_10px_purple]" />
                    </div>
                    <div className="absolute -bottom-12 left-1/2 -translate-x-1/2 px-4 py-1.5 bg-violet-700 rounded-full shadow-lg shadow-violet-200/50 flex flex-col items-center whitespace-nowrap">
                      <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-l-transparent border-r-4 border-r-transparent border-b-[8px] border-b-violet-700" />
                      <span className="text-[10px] font-black text-white uppercase leading-none">{currentSignalName}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
          
          <div className="absolute top-1/2 left-0 w-full h-[1px] bg-gray-200/50 pointer-events-none" />
        </div>
      </div>

      {/* Legenda Estática (Não Clicável) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 pt-6 border-t border-gray-50 mt-auto">
        {NATURE_TYPES.map((nature) => (
          <div
            key={nature.id}
            className="flex items-center gap-2 p-3 rounded-2xl border border-gray-50 bg-gray-50/20 group hover:bg-gray-50 transition-colors"
          >
            <div 
              className="w-2.5 h-2.5 rounded-full shrink-0 shadow-sm"
              style={{ backgroundColor: nature.color }}
            />
            <span className="text-[9.5px] font-black uppercase tracking-tight text-gray-400 group-hover:text-gray-600 transition-colors">
              {nature.label}
            </span>
          </div>
        ))}
      </div>

      {/* Bottom Detail */}
      <div className="pt-6">
        <div className="bg-gray-50/50 rounded-[32px] p-6 border border-gray-100 flex flex-col md:flex-row gap-6">
          <div className="flex-1 space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-white rounded-2xl shadow-sm border border-gray-100">
                <Target size={20} className="text-emerald-500" />
              </div>
              <div>
                <h4 className="text-lg font-black text-[#1e1b4b] leading-none mb-1">Diagnóstico de Natureza</h4>
                <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Atribuição Dominante</span>
              </div>
            </div>
            <p className="text-xs text-gray-500 font-medium leading-relaxed">
              {selectedSignalId ? (
                <>
                  O posicionamento do sinal <span className="text-violet-600 font-bold">{currentSignalName}</span> no quadrante <span className="text-violet-600 font-bold">{activeSignalNature?.label}</span> revela uma dinâmica de <span className="text-gray-600 font-bold">{activeSignalNature?.description.toLowerCase()}</span>. 
                  Comparado à sua marca (<span className="text-emerald-600 font-bold">{activeBrandNature.label}</span>), este sinal oferece um território de {selectedData?.nature === activeBrandNature.id ? 'sinergia direta' : 'oportunidade complementar'}.
                </>
              ) : (
                <>
                  O posicionamento centralizado no quadrante <span className="text-emerald-600 font-bold">Orgânico</span> revela uma alta aderência cultural, indicando que sua marca ressoa nativamente nos Clusters sem dependência de bots ou impulsão artificial.
                </>
              )}
            </p>
          </div>

          {selectedSignalId && (
            <>
              <div className="w-[1px] h-auto bg-gray-200 hidden md:block" />
              <div className="flex gap-8 shrink-0 md:w-1/3 self-center">
                <div className="space-y-1">
                  <span className="text-[9px] font-black text-violet-600 uppercase tracking-tighter">Afinidade</span>
                  <p className="text-2xl font-black text-gray-900 leading-none">{selectedData?.affinity}%</p>
                </div>
                <div className="space-y-1">
                  <span className="text-[9px] font-black text-violet-600 uppercase tracking-tighter">Harmônica</span>
                  <p className="text-2xl font-black text-gray-900 leading-none">{selectedData?.harmonicFreq}%</p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
