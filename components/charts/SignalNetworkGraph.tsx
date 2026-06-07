"use client";

import React, { useEffect, useMemo, useState } from 'react';
import { Filter, Share2, Download, Maximize2, Info, Search, Zap, Activity, X, ArrowRight, MousePointer2, TrendingUp } from 'lucide-react';
import Link from 'next/link';

interface Node {
  id: string;
  label: string;
  size: number;
  color: string;
  x: number;
  y: number;
  category: 'Sociocultural' | 'Econômico' | 'Ambiental' | 'Emocional';
  volume: number;
  tension: 'Baixa' | 'Média' | 'Alta';
  momentum: number;
  insight: string;
  harmonicFreq: number;
  affinity: number;
}

const MOCK_NODES: Node[] = [
  { id: '1', label: 'Festival Almoço no Coreto', size: 45, color: '#10b981', x: 300, y: 120, category: 'Sociocultural', volume: 2847, tension: 'Média', momentum: 78, insight: 'Engajamento massivo em festivais regionais.', harmonicFreq: 84.5, affinity: 92 },
  { id: '2', label: 'Dancinha Viral Sertaneja', size: 35, color: '#f59e0b', x: 480, y: 225, category: 'Econômico', volume: 1920, tension: 'Alta', momentum: 85, insight: 'Conversão em bens de consumo imediato.', harmonicFreq: 72.1, affinity: 88 },
  { id: '3', label: 'Robô de Suporte em Zap', size: 28, color: '#3b82f6', x: 120, y: 225, category: 'Emocional', volume: 1540, tension: 'Baixa', momentum: 92, insight: 'Adoção tech sem fricção cultural.', harmonicFreq: 95.8, affinity: 97 },
  { id: '4', label: 'Painel Solar Comunitário', size: 30, color: '#ef4444', x: 300, y: 350, category: 'Ambiental', volume: 1200, tension: 'Média', momentum: 65, insight: 'Sustentabilidade via economia solidária.', harmonicFreq: 64.2, affinity: 75 },
  { id: '5', label: 'Revenda de Tênis Usado', size: 40, color: '#3b82f6', x: 180, y: 280, category: 'Emocional', volume: 2100, tension: 'Alta', momentum: 78, insight: 'Circularidade em alta na periferia.', harmonicFreq: 88.4, affinity: 91 },
];

const TENSION_COLORS = {
  'Baixa': '#10b981',
  'Média': '#f59e0b',
  'Alta': '#ef4444'
};

const CATEGORY_COLORS = {
  'Sociocultural': '#3b82f6',
  'Econômico': '#a855f7',
  'Ambiental': '#10b981',
  'Emocional': '#f59e0b'
};

interface SignalNetworkGraphProps {
  onNodeClick?: (nodeId: string | null) => void;
  signals?: Node[]; 
}

export default function SignalNetworkGraph({ onNodeClick, signals }: SignalNetworkGraphProps) {
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const nodes = signals || MOCK_NODES; 
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [activeTab, setActiveTab] = useState<'network' | 'segments'>('network');

  const handleNodeClick = (node: Node) => {
    setSelectedNode(node);
    if (onNodeClick) onNodeClick(node.id);
  };

  // Melhorar o cálculo de conexões sugerindo afinidade semântica
  const ADJACENCY = useMemo(() => {
    const adj: Record<string, string[]> = {};
    const baseNodes = signals || MOCK_NODES;
    baseNodes.forEach(n => {
      // Conecta nós da mesma categoria
      adj[n.id] = baseNodes.filter(other => other.id !== n.id && other.category === n.category).map(other => other.id);
    });
    return adj;
  }, [signals]);

  return (
    <div className="relative h-full animate-in fade-in duration-700">
      <div className="bg-white rounded-[40px] border border-gray-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] overflow-hidden flex flex-col h-[750px]">
        {/* Header Superior - Ultra High Fidelity */}
        <div className="p-8 border-b border-gray-50 flex items-center justify-between bg-white/50 backdrop-blur-xl sticky top-0 z-30">
          <div className="flex items-center gap-6">
            <div className="flex flex-col">
              <div className="flex items-center gap-3 mb-1.5">
                <div className="w-2 h-8 bg-violet-600 rounded-full" />
                <h2 className="text-2xl font-black text-gray-900 tracking-tight">Mapa de Sinais: Rede de Conexões</h2>
              </div>
              <p className="text-[13px] text-gray-400 font-medium italic pl-5 line-clamp-1 max-w-[500px]">
                Geometria de adjacência baseada em afinidade semântica, círculos culturais e pulsão latente de mercado.
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <button className="p-3.5 text-gray-400 hover:text-violet-600 hover:bg-violet-50 rounded-2xl transition-all border border-gray-100 group">
              <Search size={20} strokeWidth={2.5} className="group-hover:scale-110 transition-transform" />
            </button>
            <button className="p-3.5 text-gray-400 hover:text-violet-600 hover:bg-violet-50 rounded-2xl transition-all border border-gray-100 group">
              <Share2 size={20} strokeWidth={2.5} className="group-hover:scale-110 transition-transform" />
            </button>
            <button className="h-12 px-6 bg-gray-900 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-black transition-all shadow-lg shadow-black/10">
              Gerar Relatório
            </button>
          </div>
        </div>

        <div className="flex flex-1 overflow-hidden relative">
          {/* Main Visualizer Area */}
          <div className="flex-1 bg-[#FDFDFF] relative overflow-hidden group/canvas">
            {/* Compass and Background Grid */}
            <div className="absolute inset-0 pointer-events-none">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-violet-50/30 via-transparent to-transparent opacity-60" />
              <div className="absolute inset-0" style={{ backgroundImage: 'radial-gradient(#E5E7EB 1.2px, transparent 1.2px)', backgroundSize: '48px 48px', opacity: 0.35 }} />
              
              <div className="absolute top-1/2 left-0 w-full h-[1.5px] bg-gradient-to-r from-transparent via-gray-200/50 to-transparent" />
              <div className="absolute left-1/2 top-0 w-[1.5px] h-full bg-gradient-to-b from-transparent via-gray-200/50 to-transparent" />
              
              {/* Pontos Cardinais com Design Refinado */}
              <div className="absolute top-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
                <div className="px-4 py-1.5 bg-white border border-gray-100 rounded-full shadow-md backdrop-blur-md">
                  <span className="text-[10px] font-black uppercase tracking-[0.25em] text-gray-400 flex items-center gap-2">
                    <Activity size={12} className="text-blue-500" /> Norte: Sociocultural
                  </span>
                </div>
              </div>

              <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
                <div className="px-4 py-1.5 bg-white border border-gray-100 rounded-full shadow-md backdrop-blur-md">
                  <span className="text-[10px] font-black uppercase tracking-[0.25em] text-gray-400 flex items-center gap-2">
                    <Activity size={12} className="text-emerald-500" /> Sul: Ambiental
                  </span>
                </div>
              </div>

              <div className="absolute left-12 top-1/2 -translate-y-1/2 flex flex-col items-center -rotate-90">
                <div className="px-4 py-1.5 bg-white border border-gray-100 rounded-full shadow-md backdrop-blur-md text-nowrap">
                  <span className="text-[10px] font-black uppercase tracking-[0.25em] text-gray-400 flex items-center gap-2">
                    <Activity size={12} className="text-amber-500" /> Oeste: Emocional
                  </span>
                </div>
              </div>

              <div className="absolute right-12 top-1/2 -translate-y-1/2 flex flex-col items-center rotate-90">
                <div className="px-4 py-1.5 bg-white border border-gray-100 rounded-full shadow-md backdrop-blur-md text-nowrap">
                  <span className="text-[10px] font-black uppercase tracking-[0.25em] text-gray-400 flex items-center gap-2">
                    <Activity size={12} className="text-purple-500" /> Leste: Econômico
                  </span>
                </div>
              </div>
            </div>

            {/* SVG Graph Layout */}
            <svg className="w-full h-full relative z-10 overflow-visible" viewBox="0 0 600 450">
              <defs>
                <radialGradient id="sphereGradient">
                  <stop offset="0%" stopColor="white" stopOpacity="1" />
                  <stop offset="70%" stopColor="#f8fafc" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#e2e8f0" stopOpacity="0.4" />
                </radialGradient>
              </defs>

              {/* Connections - Enhanced with Motion */}
              {nodes.map((node, i) => {
                const isConnected = hoveredNodeId === node.id || (hoveredNodeId && ADJACENCY[hoveredNodeId]?.includes(node.id));
                return (
                  <g key={`link-group-${i}`} className="transition-all duration-700 ease-in-out">
                    <path 
                      d={`M 300 225 Q ${(300 + node.x)/2 + 20} ${(225 + node.y)/2 - 20} ${node.x} ${node.y}`}
                      fill="none" 
                      stroke={isConnected ? "#7c3aed" : "#cbd5e1"} 
                      strokeWidth={isConnected ? "2.5" : "1"} 
                      strokeDasharray={isConnected ? "0" : "6 6"}
                      strokeOpacity={isConnected ? "0.8" : "0.15"}
                      className="transition-all duration-500"
                    />
                  </g>
                );
              })}

              {nodes.map((node) => {
                const isHovered = hoveredNodeId === node.id;
                const isRelated = hoveredNodeId && ADJACENCY[hoveredNodeId]?.includes(node.id);
                const isDimmed = hoveredNodeId && !isHovered && !isRelated;

                return (
                  <g 
                    key={node.id} 
                    className={`cursor-pointer group select-none transition-all duration-500 ease-in-out ${isDimmed ? 'opacity-20 blur-[1px]' : 'opacity-100'}`}
                    onClick={() => handleNodeClick(node)}
                    onMouseEnter={() => setHoveredNodeId(node.id)}
                    onMouseLeave={() => setHoveredNodeId(null)}
                  >
                    {/* Node Core - Color strictly defined by Tension Metrics */}
                    <circle 
                      cx={node.x} 
                      cy={node.y} 
                      r={(node.volume / 100) + 2} 
                      fill={TENSION_COLORS[node.tension]} 
                      className="transition-all duration-300 drop-shadow-sm"
                    />

                    {/* Category Identifier (Small white core dot for clarity) */}
                    <circle 
                      cx={node.x} 
                      cy={node.y} 
                      r={isHovered ? 4 : 2} 
                      fill="white"
                      fillOpacity={0.8}
                      className="transition-all duration-300"
                    />

                    {/* Enhanced Labeling */}
                    <rect 
                      x={node.x - (node.label.length * 3.5)} 
                      y={node.y + (node.volume / 100) + 8} 
                      width={node.label.length * 7} 
                      height={18} 
                      rx={6} 
                      fill={isHovered ? "#1e1b4b" : "white"} 
                      fillOpacity={isHovered ? "1" : "0.7"}
                      className="transition-all duration-300"
                    />
                    <text 
                      x={node.x} 
                      y={node.y + (node.volume / 100) + 21} 
                      textAnchor="middle" 
                      className={`text-[9px] font-black uppercase tracking-tight transition-all duration-300 ${isHovered ? 'fill-white' : 'fill-gray-900'}`}
                    >
                      {node.label}
                    </text>
                  </g>
                );
              })}
            </svg>

            {/* Hover Tooltip HUD */}
            {hoveredNodeId && (
              (() => {
                const node = nodes.find(n => n.id === hoveredNodeId);
                if (!node) return null;
                const isRight = node.x > 300;
                return (
                  <div className="absolute z-50 pointer-events-none transition-all duration-300 transform scale-100" style={{ left: isRight ? node.x - 240 : node.x + 30, top: node.y - 40, width: '220px' }}>
                    <div className="bg-gray-900/90 backdrop-blur-2xl border border-gray-700/50 rounded-[28px] p-5 shadow-2xl space-y-4">
                      <div className="flex justify-between items-start gap-4 border-b border-gray-700/40 pb-3">
                        <div className="flex flex-col gap-0.5">
                          <span className="text-[8px] font-black text-gray-500 uppercase tracking-widest">Tensão Contextual</span>
                          <div className="flex items-center gap-1.5">
                            <div className="h-2 w-2 rounded-full" style={{ backgroundColor: TENSION_COLORS[node.tension] }} />
                            <span className="text-[11px] font-black text-white uppercase">{node.tension}</span>
                          </div>
                        </div>
                        <div className="flex flex-col items-end gap-0.5">
                          <span className="text-[8px] font-black text-gray-500 uppercase tracking-widest">Volume Total</span>
                          <span className="text-[12px] font-black text-emerald-400 tabular-nums">
                            {mounted ? node.volume.toLocaleString() : node.volume.toString()}
                          </span>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center gap-1.5 text-violet-400">
                          <Zap size={12} fill="currentColor" />
                          <span className="text-[9px] font-black uppercase tracking-wider">Direcionamento de Valor</span>
                        </div>
                        <p className="text-[10px] text-gray-300 leading-relaxed font-medium">{node.insight}</p>
                      </div>
                      <div className="flex justify-between items-center bg-white/5 rounded-xl px-3 py-2 border border-white/10">
                         <span className="text-[8px] font-bold text-gray-400 uppercase">Harmônica</span>
                         <span className="text-[10px] font-black text-white">{node.harmonicFreq}%</span>
                      </div>
                    </div>
                  </div>
                );
              })()
            )}

            {/* Zoom Controls - Bottom Left */}
            <div className="absolute bottom-6 left-6 z-20 flex flex-col gap-2">
              <button className="w-10 h-10 bg-white border border-gray-100 rounded-xl shadow-lg flex items-center justify-center text-gray-500 hover:text-violet-600 hover:bg-violet-50 transition-all active:scale-95 group">
                <span className="text-xl font-bold group-hover:scale-110 transition-transform">+</span>
              </button>
              <button className="w-10 h-10 bg-white border border-gray-100 rounded-xl shadow-lg flex items-center justify-center text-gray-500 hover:text-violet-600 hover:bg-violet-50 transition-all active:scale-95 group">
                <span className="text-xl font-bold group-hover:scale-110 transition-transform">−</span>
              </button>
            </div>

            {/* Quick Stats - Bottom Right - Micro Minimalist */}
            <div className="absolute bottom-6 right-6 z-20 flex items-center gap-3 py-1.5 px-3 bg-white/20 backdrop-blur-[2px] rounded-full border border-gray-100/20">
                <div className="flex items-center gap-1">
                  <span className="text-[10px] font-black text-gray-900 tabular-nums">12</span>
                  <span className="text-[6px] font-black text-gray-400 uppercase tracking-tighter">Sinais</span>
                </div>
                <div className="w-[1px] h-1.5 bg-gray-200/30" />
                <div className="flex items-center gap-1">
                  <span className="text-[10px] font-black text-gray-900 tabular-nums">48</span>
                  <span className="text-[6px] font-black text-gray-400 uppercase tracking-tighter">Conexões</span>
                </div>
                <div className="w-[1px] h-1.5 bg-gray-200/30" />
                <div className="flex items-center gap-1">
                  <span className="text-[10px] font-black text-gray-900 tabular-nums">9.4k</span>
                  <span className="text-[6px] font-black text-gray-400 uppercase tracking-tighter">Menções</span>
                </div>
            </div>
          </div>

          {/* Right Sidebar - Maximalist */}
          <div className="w-[340px] border-l border-gray-100 flex flex-col bg-white p-6 space-y-6 overflow-hidden">
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-3.5 bg-violet-50 rounded-2xl border border-violet-100 mb-2">
                 <MousePointer2 size={16} className="text-violet-600 shrink-0" />
                 <p className="text-[10px] font-bold text-violet-700 leading-tight">Clique em um sinal para mais detalhes</p>
              </div>

              <div className="flex items-center justify-between px-1">
                <h3 className="text-[11px] font-black text-gray-400 uppercase tracking-[0.2em]">Nível de Tensão</h3>
                <Info size={14} className="text-gray-300" />
              </div>

              <div className="grid grid-cols-1 gap-2.5">
                {Object.entries(TENSION_COLORS).map(([label, color]) => (
                  <div key={label} className="flex items-center justify-between group cursor-help p-2 hover:bg-gray-50 rounded-xl transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="h-1.5 w-6 rounded-full transition-all group-hover:w-8" style={{ backgroundColor: color }} />
                      <span className="text-[10px] font-black text-gray-500 uppercase tracking-tight">{label}</span>
                    </div>
                    <span className="text-[9px] font-bold text-gray-300 group-hover:text-gray-900 transition-colors">
                      {label === 'Alta' ? 'Urgência' : label === 'Média' ? 'Maturação' : 'Estável'}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-4 pt-6 border-t border-gray-50 flex-1 flex flex-col justify-center">
              <h3 className="text-[11px] font-black text-gray-400 uppercase tracking-[0.2em] px-1">Métricas da Rede</h3>
              
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-violet-50/50 rounded-[24px] p-4 border border-violet-100/50 flex flex-col gap-1 relative overflow-hidden group">
                  <p className="text-[9px] font-black text-violet-400 uppercase tracking-widest relative z-10">Momentum</p>
                  <div className="flex items-baseline gap-1 relative z-10">
                    <span className="text-2xl font-black text-violet-900 tracking-tighter">79.6</span>
                  </div>
                </div>

                <div className="bg-emerald-50/50 rounded-[24px] p-4 border border-emerald-100/50 flex flex-col gap-1 relative overflow-hidden group">
                  <p className="text-[9px] font-black text-emerald-400 uppercase tracking-widest relative z-10">Tensão</p>
                  <div className="flex items-baseline gap-1 relative z-10">
                    <span className="text-2xl font-black text-emerald-900 tracking-tighter">Média</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-900 rounded-[24px] p-5 shadow-lg shadow-gray-200 relative overflow-hidden mt-2">
                <div className="absolute top-0 right-0 w-24 h-24 bg-violet-500/10 blur-2xl -mr-12 -mt-12" />
                <div className="space-y-3 relative z-10">
                   <div className="flex justify-between items-center">
                      <span className="text-[9px] font-black text-gray-400 uppercase tracking-wider">Coerência da Rede</span>
                      <div className="px-2 py-0.5 bg-emerald-500/20 rounded-full">
                        <span className="text-[8px] font-black text-emerald-400 uppercase">Alta</span>
                      </div>
                   </div>
                   <div className="flex items-end gap-3">
                      <div className="h-1.5 flex-1 bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-violet-500 to-emerald-500 w-[79%]" />
                      </div>
                      <span className="text-[10px] font-black text-white tabular-nums">79%</span>
                   </div>
                </div>
              </div>
            </div>

            <div className="mt-auto pt-4 border-t border-gray-50 flex items-center justify-center opacity-20">
               <p className="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em]">Culture Intelligence v9.7</p>
            </div>
          </div>
        </div>
      </div>

      {/* Full Modal Detail */}
      {selectedNode && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-gray-900/40 backdrop-blur-md animate-in fade-in duration-300">
          <div className="bg-white w-full max-w-5xl rounded-[60px] shadow-[0_32px_120px_rgb(0,0,0,0.25)] overflow-hidden flex flex-col animate-in zoom-in-95 ease-out duration-300">
            <div className="p-10 border-b border-gray-50 flex justify-between items-start">
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                   <span className="px-4 py-1.5 text-white text-[11px] font-black rounded-full uppercase tracking-[0.2em]" style={{ backgroundColor: CATEGORY_COLORS[selectedNode.category] }}>{selectedNode.category}</span>
                   <div className="px-3 py-1 bg-gray-50 border border-gray-100 rounded-full text-[10px] font-bold text-gray-400 uppercase">Ref: #{selectedNode.id}</div>
                </div>
                <div>
                  <h2 className="text-5xl font-black text-[#1e1b4b] tracking-tighter mb-2">{selectedNode.label}</h2>
                  <div className="flex items-center gap-2 text-gray-400">
                     <TrendingUp size={16} className="text-emerald-500" />
                     <span className="text-sm font-medium italic">Sinal em fase de aceleração exponencial no território brasileiro.</span>
                  </div>
                </div>
              </div>
              <button 
                onClick={() => setSelectedNode(null)} 
                className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center text-gray-400 border border-gray-100 transition-all active:scale-90"
              >
                <X size={28} strokeWidth={2.5} />
              </button>
            </div>
            <div className="p-10 grid grid-cols-12 gap-8">
               <div className="col-span-4 bg-gray-50 rounded-[48px] p-10 border border-gray-100 flex flex-col items-center justify-center text-center space-y-4 shadow-inner">
                  <p className="text-[12px] font-black text-gray-400 uppercase tracking-[0.3em]">Momentum</p>
                  <p className="text-8xl font-black text-[#1e1b4b] tracking-tighter">{selectedNode.momentum}</p>
               </div>
               <div className="col-span-4 bg-gray-50 rounded-[48px] p-10 border border-gray-100 flex flex-col items-center justify-center text-center space-y-4 shadow-inner">
                  <p className="text-[12px] font-black text-gray-400 uppercase tracking-[0.3em]">Volume Total</p>
                  <p className="text-8xl font-black text-[#1e1b4b] tracking-tighter">
                    {mounted ? selectedNode.volume.toLocaleString() : selectedNode.volume.toString()}
                  </p>
               </div>
               <div className="col-span-4 bg-violet-700 rounded-[48px] p-10 text-white flex flex-col justify-between shadow-2xl shadow-violet-200">
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 mb-4">
                      <Zap size={24} fill="currentColor" strokeWidth={0} />
                      <p className="text-[12px] font-black text-violet-200 uppercase tracking-[0.3em]">Insight Estratégico</p>
                    </div>
                    <p className="text-lg font-medium leading-relaxed italic opacity-90">"{selectedNode.insight}"</p>
                  </div>
                  <Link 
                    href="/dashboard/signals"
                    className="mt-8 h-14 bg-white text-violet-700 w-full rounded-2xl text-[11px] font-black uppercase tracking-widest hover:bg-violet-50 transition-all flex items-center justify-center gap-2"
                  >
                    Explorar Origem <ArrowRight size={16} />
                  </Link>
               </div>
               <div className="col-span-12 grid grid-cols-3 gap-8 mt-4">
                  <div className="p-6 bg-white border border-gray-100 rounded-3xl flex items-center justify-between">
                     <span className="text-[11px] font-black text-gray-400 uppercase">Afinidade</span>
                     <span className="text-xl font-black text-gray-900">{selectedNode.affinity}%</span>
                  </div>
                  <div className="p-6 bg-white border border-gray-100 rounded-3xl flex items-center justify-between">
                     <span className="text-[11px] font-black text-gray-400 uppercase">Harmônica</span>
                     <span className="text-xl font-black text-gray-900">{selectedNode.harmonicFreq}%</span>
                  </div>
                  <div className="p-6 bg-white border border-gray-100 rounded-3xl flex items-center justify-between">
                     <span className="text-[11px] font-black text-gray-400 uppercase">Tensão</span>
                     <span className={`text-xl font-black ${selectedNode.tension === 'Alta' ? 'text-red-500' : 'text-emerald-500'}`}>{selectedNode.tension}</span>
                  </div>
               </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
