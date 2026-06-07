"use client";
import React, { useEffect, useState } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Cell,
  PieChart,
  Pie
} from 'recharts';
import { Share2, Globe, MessageSquare, Instagram, Zap, Database, ArrowUpRight } from 'lucide-react';
import Link from 'next/link';

const CHANNEL_DATA = [
  { name: 'TikTok', value: 4200, color: '#000000', icon: <Zap size={14} />, percentage: '32.8%', insight: 'Volume massivo de sinais de "entretenimento rápido" detectados.' },
  { name: 'Instagram', value: 3800, color: '#E1306C', icon: <Instagram size={14} />, percentage: '29.7%', insight: 'Alta correlação com clusters de estética e lifestyle orgânico.' },
  { name: 'X (Twitter)', value: 2100, color: '#1DA1F2', icon: <Share2 size={14} />, percentage: '16.4%', insight: 'Ponto focal de conversas críticas e eventos em tempo real.' },
  { name: 'Google Trends', value: 1500, color: '#4285F4', icon: <Globe size={14} />, percentage: '11.7%', insight: 'Sinais consistentes de busca ativa por soluções práticas.' },
  { name: 'News/Web', value: 1200, color: '#64748b', icon: <Database size={14} />, percentage: '9.4%', insight: 'Narrativas de autoridade e consolidação de tendências.' },
];

export default function SignalChannelDistribution() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="bg-white rounded-[40px] border border-gray-100 shadow-sm p-8 space-y-8 h-full flex flex-col transition-all duration-500 hover:border-violet-100">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div className="space-y-1">
          <h2 className="text-2xl font-black text-[#1e1b4b] tracking-tight text-left">Distribuição por Canais (API)</h2>
          <p className="text-sm text-gray-400 font-medium text-left italic">
            Origem volumétrica dos sinais processados
          </p>
        </div>
        <div className="bg-emerald-50 px-4 py-2 rounded-2xl border border-emerald-100 flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[10px] font-black text-emerald-700 uppercase tracking-widest leading-none">Live Monitoring</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Lado Esquerdo: Visualização de Barras Custom e Lista */}
        <div className="lg:col-span-7 space-y-6">
          <div className="space-y-4">
            {CHANNEL_DATA.map((channel) => (
              <div key={channel.name} className="group relative">
                <div className="flex justify-between items-center mb-1.5 px-1">
                  <div className="flex items-center gap-2">
                    <div 
                      className="p-1.5 rounded-lg flex items-center justify-center text-white shadow-sm transition-transform group-hover:scale-110"
                      style={{ backgroundColor: channel.color }}
                    >
                      {channel.name === 'TikTok' && <Zap size={12} />}
                      {channel.name === 'Instagram' && <Instagram size={12} />}
                      {channel.name === 'X (Twitter)' && <Share2 size={12} />}
                      {channel.name === 'Google Trends' && <Globe size={12} />}
                      {channel.name === 'News/Web' && <Database size={12} />}
                    </div>
                    <span className="text-[13px] font-black text-gray-700 uppercase tracking-tight">{channel.name}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-black text-gray-900">{mounted ? channel.value.toLocaleString() : channel.value.toString()}</span>
                    <span className="text-[10px] font-bold text-gray-400 ml-2 uppercase">{channel.percentage}</span>
                  </div>
                </div>
                <div className="h-2.5 w-full bg-gray-50 rounded-full overflow-hidden border border-gray-100/50 cursor-help">
                  <div 
                    className="h-full rounded-full transition-all duration-1000 ease-out shadow-[0_0_12px_rgba(0,0,0,0.05)]"
                    style={{ 
                      width: channel.percentage,
                      backgroundColor: channel.color,
                      opacity: 0.85
                    }}
                  />
                </div>

                {/* Tooltip Custom / Pop-up ao passar o mouse */}
                <div className="absolute left-0 bottom-full mb-4 w-64 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-[400ms] z-[100] translate-y-2 group-hover:translate-y-0">
                  <div className="bg-[#1e1b4b] text-white p-5 rounded-[32px] shadow-2xl border border-white/10 relative overflow-hidden backdrop-blur-xl">
                    {/* Glow effect */}
                    <div className="absolute -right-4 -top-4 w-16 h-16 bg-violet-500/20 blur-2xl rounded-full" />
                    
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-violet-300 mb-2">Insight de Canal</p>
                    <p className="text-xs font-medium leading-relaxed mb-5 opacity-90">
                      {channel.insight}
                    </p>
                    
                    <Link 
                      href="/dashboard/trends" 
                      className="flex items-center justify-between bg-violet-600/20 hover:bg-violet-600 text-white px-4 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest group/btn transition-all border border-violet-500/30"
                    >
                      Explorar Tendências
                      <ArrowUpRight size={14} className="group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5 transition-transform" />
                    </Link>
                    
                    {/* Arrow down */}
                    <div className="absolute -bottom-1 left-6 w-3 h-3 bg-[#1e1b4b] rotate-45 border-r border-b border-white/10" />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="pt-4 border-t border-gray-50">
             <div className="p-4 bg-violet-50/50 rounded-3xl border border-violet-100/50">
                <p className="text-[10px] font-black text-violet-600 uppercase tracking-[0.2em] mb-2">Insight de Canal</p>
                <p className="text-xs text-violet-950 font-medium leading-relaxed text-left">
                  O <span className="font-black">TikTok</span> mantém a liderança em volume bruto, mas o <span className="font-black">Instagram</span> apresenta maior correlação com os clusters de comportamento orgânico desta semana.
                </p>
             </div>
          </div>
        </div>

        {/* Lado Direito: Mini Donut Chart */}
        <div className="lg:col-span-5 h-[280px] relative flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={280}>
            <PieChart>
              <Pie
                data={CHANNEL_DATA}
                cx="50%"
                cy="50%"
                innerRadius={65}
                outerRadius={95}
                paddingAngle={8}
                dataKey="value"
                stroke="none"
              >
                {CHANNEL_DATA.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} opacity={0.9} className="cursor-pointer" />
                ))}
              </Pie>
              <Tooltip 
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-[#1e1b4b] text-white p-5 rounded-[32px] shadow-2xl border border-white/10 w-64 backdrop-blur-xl">
                         <div className="flex items-center gap-2 mb-2">
                           <div className="w-2 h-2 rounded-full" style={{ backgroundColor: data.color }} />
                           <span className="text-[10px] font-black uppercase tracking-widest">{data.name}</span>
                         </div>
                         <p className="text-[11px] font-medium leading-relaxed mb-5 opacity-80 italic">
                            "{data.insight}"
                         </p>
                         <Link 
                            href="/dashboard/trends" 
                            className="flex items-center justify-between bg-violet-600 text-white px-4 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest group/link hover:bg-violet-400 transition-all shadow-[0_4px_12px_rgba(124,58,237,0.3)]"
                         >
                            Explorar Tendências
                            <ArrowUpRight size={14} className="group-hover/link:translate-x-0.5 group-hover/btn:-translate-y-0.5 transition-transform" />
                         </Link>
                      </div>
                    );
                  }
                  return null;
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          
          {/* Central Label */}
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Total</span>
            <span className="text-2xl font-black text-gray-900 tracking-tighter">12.8k</span>
            <span className="text-[8px] font-bold text-emerald-500 mt-1 uppercase">Signals API</span>
          </div>
        </div>
      </div>
    </div>
  );
}
