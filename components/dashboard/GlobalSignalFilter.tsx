"use client";
import React, { useState } from 'react';
import { Filter, Calendar, ChevronDown, Check, Search } from 'lucide-react';

interface GlobalSignalFilterProps {
  onSignalChange?: (signalName: string) => void;
}

export default function GlobalSignalFilter({ onSignalChange }: GlobalSignalFilterProps) {
  const [selectedRange, setSelectedRange] = useState('Últimas 24h');
  const [selectedSource, setSelectedSource] = useState('Todas as Fontes');
  const [selectedSignal, setSelectedSignal] = useState('Todos os Sinais');
  const [showRangeDrop, setShowRangeDrop] = useState(false);
  const [showSourceDrop, setShowSourceDrop] = useState(false);
  const [showSignalDrop, setShowSignalDrop] = useState(false);

  const ranges = ['Últimas 24h', 'Últimos 7 dias', 'Últimos 30 dias', 'Personalizado'];
  const sources = ['Todas as Fontes', 'TikTok', 'Instagram', 'X (Twitter)', 'Google Trends', 'News'];
  const signalNames = [
    'Todos os Sinais', 
    'Brasilidade', 
    'Tecnologia', 
    'Sustentabilidade', 
    'Sertanejo Pop', 
    'IA Generativa', 
    'Ancestralidade',
    'Economia Circular'
  ];

  return (
    <div className="flex flex-wrap items-center gap-3 py-4 border-y border-gray-100 mb-8">
      <div className="flex items-center gap-2 text-gray-400 mr-2">
        <Filter size={14} className="text-violet-600" />
        <span className="text-[10px] font-black uppercase tracking-widest">Filtro Global de Sinais</span>
      </div>

      {/* 1. Date Range Selector */}
      <div className="relative">
        <button 
          onClick={() => { setShowRangeDrop(!showRangeDrop); setShowSourceDrop(false); setShowSignalDrop(false); }}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-100 rounded-2xl text-[11px] font-black text-gray-700 hover:border-violet-200 transition-all shadow-sm"
        >
          <Calendar size={12} className="text-gray-400" />
          {selectedRange}
          <ChevronDown size={12} className={`text-gray-400 transition-transform ${showRangeDrop ? 'rotate-180' : ''}`} />
        </button>
        {showRangeDrop && (
          <div className="absolute top-full left-0 mt-2 w-48 bg-white border border-gray-100 rounded-2xl shadow-xl z-50 overflow-hidden py-1">
            {ranges.map(r => (
              <button 
                key={r}
                onClick={() => { setSelectedRange(r); setShowRangeDrop(false); }}
                className="w-full text-left px-4 py-2.5 text-[11px] font-bold text-gray-600 hover:bg-violet-50 hover:text-violet-700 flex items-center justify-between"
              >
                {r}
                {selectedRange === r && <Check size={10} className="text-violet-600" />}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 2. Source Selector */}
      <div className="relative">
        <button 
          onClick={() => { setShowSourceDrop(!showSourceDrop); setShowRangeDrop(false); setShowSignalDrop(false); }}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-100 rounded-2xl text-[11px] font-black text-gray-700 hover:border-violet-200 transition-all shadow-sm"
        >
          <div className="flex -space-x-1.5 mr-1">
             <div className="h-3.5 w-3.5 rounded-full bg-blue-500 border border-white" />
             <div className="h-3.5 w-3.5 rounded-full bg-rose-500 border border-white" />
             <div className="h-3.5 w-3.5 rounded-full bg-sky-500 border border-white" />
          </div>
          {selectedSource}
          <ChevronDown size={12} className={`text-gray-400 transition-transform ${showSourceDrop ? 'rotate-180' : ''}`} />
        </button>
        {showSourceDrop && (
          <div className="absolute top-full left-0 mt-2 w-48 bg-white border border-gray-100 rounded-2xl shadow-xl z-50 overflow-hidden py-1">
            {sources.map(s => (
              <button 
                key={s}
                onClick={() => { setSelectedSource(s); setShowSourceDrop(false); }}
                className="w-full text-left px-4 py-2.5 text-[11px] font-bold text-gray-600 hover:bg-violet-50 hover:text-violet-700 flex items-center justify-between"
              >
                {s}
                {selectedSource === s && <Check size={10} className="text-violet-600" />}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 3. Signal Capture Selector (Link to Metric 1) */}
      <div className="relative">
        <button 
          onClick={() => { setShowSignalDrop(!showSignalDrop); setShowRangeDrop(false); setShowSourceDrop(false); }}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-100 rounded-2xl text-[11px] font-black text-gray-700 hover:border-violet-200 transition-all shadow-sm"
        >
          <Search size={12} className="text-blue-500" />
          {selectedSignal}
          <ChevronDown size={12} className={`text-gray-400 transition-transform ${showSignalDrop ? 'rotate-180' : ''}`} />
        </button>
        {showSignalDrop && (
          <div className="absolute top-full left-0 mt-2 w-56 bg-white border border-gray-100 rounded-2xl shadow-xl z-50 overflow-hidden py-1">
            <div className="px-4 py-2 bg-gray-50 text-[9px] font-black text-gray-400 uppercase tracking-widest border-b border-gray-100">Filtrar por Nome do Sinal</div>
            {signalNames.map(s => (
              <button 
                key={s}
                onClick={() => { 
                  setSelectedSignal(s); 
                  setShowSignalDrop(false); 
                  if (onSignalChange) onSignalChange(s);
                }}
                className="w-full text-left px-4 py-2.5 text-[11px] font-bold text-gray-600 hover:bg-blue-50 hover:text-blue-700 flex items-center justify-between"
              >
                {s}
                {selectedSignal === s && <Check size={10} className="text-blue-600" />}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Quick Visual Stats */}
      <div className="hidden lg:flex items-center gap-4 ml-auto">
         <div className="flex items-center gap-2">
            <div className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            <span className="text-[10px] font-bold text-gray-400">Fluxo Estável</span>
         </div>
         <div className="flex items-center gap-2">
            <div className="h-1.5 w-1.5 rounded-full bg-amber-500" />
            <span className="text-[10px] font-bold text-gray-400">Anomalias: 2 Detetadas</span>
         </div>
      </div>
    </div>
  );
}
