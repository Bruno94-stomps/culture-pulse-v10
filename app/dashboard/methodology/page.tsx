"use client";

import React from 'react';
import { 
  BookOpen, 
  Target, 
  TrendingUp, 
  Zap, 
  Binary, 
  ArrowLeft,
  ChevronRight,
  ShieldCheck
} from 'lucide-react';
import Link from 'next/link';

export default function MethodologyDeepDive() {
  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-violet-950 text-white py-16 px-6">
        <div className="max-w-4xl mx-auto">
          <Link href="/dashboard" className="inline-flex items-center gap-2 text-violet-300 hover:text-white transition-colors mb-8 group">
            <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
            Voltar ao Dashboard
          </Link>
          <div className="flex items-center gap-4 mb-4 text-violet-400 font-bold uppercase tracking-widest text-xs">
            <Binary size={18} />
            Futuruma Pulse Engine V10.4
          </div>
          <h1 className="text-5xl font-black tracking-tight mb-6">
            Deep-Dive <span className="text-violet-400">Metodológico</span>
          </h1>
          <p className="text-xl text-violet-100/80 max-w-2xl leading-relaxed font-medium">
            Entenda a ciência de dados e a teoria cultural por trás de cada métrica do seu dashboard.
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto -mt-10 px-6 space-y-8">
        {/* Core Algorithm: Alpha */}
        <div className="bg-white rounded-3xl p-10 shadow-xl border border-gray-100">
          <div className="flex items-center gap-3 mb-8">
            <div className="bg-violet-100 p-3 rounded-2xl text-violet-600">
              <Target size={28} strokeWidth={2.5} />
            </div>
            <div>
              <h2 className="text-2xl font-black text-gray-900 leading-none">Cultural Alpha (α)</h2>
              <p className="text-sm text-gray-400 font-medium mt-1 uppercase tracking-wider">O Motor de Geometria Semântica</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
            <div className="space-y-4">
              <p className="text-gray-600 leading-relaxed italic border-l-4 border-violet-100 pl-4 py-2">
                "O Alpha não é volume, é distância estratégica."
              </p>
              <p className="text-gray-500 text-sm leading-relaxed">
                Utilizamos o modelo <strong>BERTimbau</strong> (Large) para converter seu briefing e os sinais captados em vetores multidimensionais. O Alpha é o desvio do seu projeto em relação ao "Buraco Negro" do mainstream.
              </p>
              <div className="bg-gray-900 rounded-2xl p-6 text-center shadow-inner">
                <span className="text-violet-400 font-mono text-xl">α = 1 - (A · B / |A||B|)</span>
              </div>
            </div>
            <div className="bg-gray-50 rounded-2xl p-6 space-y-4">
              <h4 className="font-bold text-gray-900 flex items-center gap-2">
                <ShieldCheck size={16} className="text-emerald-500" />
                Interpretação Estratégica
              </h4>
              <ul className="space-y-3">
                <li className="flex gap-3 text-xs text-gray-600">
                  <span className="font-black text-violet-600">0.15</span>
                  <span><strong>Inércia:</strong> Baixo ROI de atenção. Sua marca está replicando clichês do setor.</span>
                </li>
                <li className="flex gap-3 text-xs text-gray-600">
                  <span className="font-black text-violet-600">0.85</span>
                  <span><strong>Disrupção:</strong> Alta vantagem competitiva. Vocabulário inédito no mainstream.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* IPC: Potential Index */}
        <div className="bg-white rounded-3xl p-10 shadow-xl border border-gray-100 group hover:border-violet-200 transition-colors">
          <div className="flex items-center gap-3 mb-8">
            <div className="bg-emerald-50 p-3 rounded-2xl text-emerald-600 group-hover:bg-emerald-100 transition-colors">
              <TrendingUp size={28} strokeWidth={2.5} />
            </div>
            <div>
              <h2 className="text-2xl font-black text-gray-900 leading-none">Índice IPC (Potencial Cultural)</h2>
              <p className="text-sm text-gray-400 font-medium mt-1 uppercase tracking-wider">A Métirca de Execução e Escala</p>
            </div>
          </div>

          <div className="bg-violet-900 rounded-3xl p-8 text-white mb-8 shadow-lg shadow-violet-200">
            <h3 className="text-lg font-black mb-4 flex items-center gap-2">
               A Analogia do Grande Salto
            </h3>
            <p className="text-violet-100/90 text-sm leading-relaxed">
              Imagine que o <strong>Alpha</strong> é o tamanho do salto que sua marca deu para fora do clichê. Já o <strong>Ganhos de Sinais (IPC)</strong> é a potência desse salto.
            </p>
            <div className="mt-6 grid grid-cols-2 gap-4">
              <div className="bg-white/10 rounded-xl p-4 border border-white/10">
                <p className="text-[10px] uppercase font-black tracking-widest text-violet-300">Onde você está</p>
                <p className="font-bold text-sm">Dashboard / Radar</p>
              </div>
              <div className="bg-white/10 rounded-xl p-4 border border-white/10">
                <p className="text-[10px] uppercase font-black tracking-widest text-violet-300">Potencial de Ganho</p>
                <p className="font-bold text-sm">Intelligence Bar / IPC</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-6">
            <div className="text-center p-4 bg-gray-50 rounded-2xl border border-gray-100">
              <RefreshCw size={20} className="mx-auto mb-2 text-amber-600" />
              <p className="text-[9px] font-black uppercase tracking-tight text-gray-400">Recorrência</p>
              <p className="text-xs text-gray-600 mt-1">Volume histórico no setor</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-2xl border border-gray-100">
              <Zap size={20} className="mx-auto mb-2 text-rose-600" />
              <p className="text-[9px] font-black uppercase tracking-tight text-gray-400">Reação</p>
              <p className="text-xs text-gray-600 mt-1">Resposta emocional (Twins)</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-2xl border border-gray-100">
              <BookOpen size={20} className="mx-auto mb-2 text-violet-600" />
              <p className="text-[9px] font-black uppercase tracking-tight text-gray-400">Predição</p>
              <p className="text-xs text-gray-600 mt-1">Probabilidade de escala D+90</p>
            </div>
          </div>
        </div>

        {/* Footer Navigation */}
        <div className="pt-10 flex justify-between items-center">
          <p className="text-xs text-gray-400 font-medium">
            Futuruma Framework V10.4 • © 2026 Pulse Engine
          </p>
          <Link href="/dashboard/system" className="text-violet-600 font-black text-xs uppercase tracking-widest flex items-center gap-2 hover:gap-3 transition-all underline decoration-2 underline-offset-4">
            Auditar Saúde do Sistema <ChevronRight size={14} />
          </Link>
        </div>
      </div>
    </div>
  );
}

// Helper icons
function RefreshCw(props: any) {
  return (
    <svg 
      {...props}
      width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
    >
      <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
      <path d="M21 3v5h-5" />
      <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
      <path d="M3 21v-5h5" />
    </svg>
  );
}
