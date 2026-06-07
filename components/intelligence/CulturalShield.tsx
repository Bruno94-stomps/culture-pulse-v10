"use client";

import React from 'react';

interface Alert {
  type: string;
  level: 'critical' | 'warning' | 'info';
  message: string;
  mitigation?: string;
}

interface StrategicAction {
  category?: string;
  action_type?: string;
  title: string;
  description: string;
  priority: 'High' | 'Medium' | 'Low';
  urgency?: number;
  effort?: string;
  impact_area?: string[];
  channels?: string[];
  playbook?: string[];
}

interface ShieldData {
  vulnerability_score: number;
  threats: string[];
  recommendations: string[];
}

interface CulturalShieldProps {
  shield?: ShieldData;
  alerts: Alert[];
  actions: StrategicAction[];
}

export default function CulturalShield({ shield, alerts, actions }: CulturalShieldProps) {
  const score = shield?.vulnerability_score ?? 0;
  const scorePct = (score * 100).toFixed(0);

  const getScoreColor = () => {
    if (score > 0.7) return 'text-red-500 bg-red-50 border-red-100';
    if (score > 0.4) return 'text-amber-500 bg-amber-50 border-amber-100';
    return 'text-emerald-500 bg-emerald-50 border-emerald-100';
  };

  const getLevelBadge = (level: string) => {
    switch(level) {
      case 'critical': return 'bg-red-600 text-white';
      case 'warning': return 'bg-amber-500 text-white';
      default: return 'bg-blue-500 text-white';
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Coluna 1: Status de Blindagem */}
      <div className="lg:col-span-1 space-y-6">
        <div className={`p-6 rounded-3xl border ${getScoreColor()} flex flex-col items-center text-center shadow-sm`}>
          <span className="text-sm font-bold uppercase tracking-wider mb-2">Índice de Vulnerabilidade</span>
          <div className="relative flex items-center justify-center w-32 h-32 mb-4">
            <svg className="w-full h-full transform -rotate-90">
              <circle cx="64" cy="64" r="58" stroke="currentColor" strokeWidth="8" fill="transparent" className="opacity-10" />
              <circle cx="64" cy="64" r="58" stroke="currentColor" strokeWidth="8" fill="transparent" strokeDasharray={364.4} strokeDashoffset={364.4 - (364.4 * score)} strokeLinecap="round" />
            </svg>
            <span className="absolute text-3xl font-black">{scorePct}%</span>
          </div>
          <p className="text-xs opacity-75 max-w-[200px]">
            {score > 0.7 ? "ALERTA: Sua marca está altamente exposta a ruídos culturais." : 
             score > 0.4 ? "ATENÇÃO: Existem pontos cegos que podem gerar atrito." : 
             "SAUDÁVEL: Sua estratégia está bem alinhada culturalmente."}
          </p>
        </div>

        {/* Notificações Críticas */}
        <div className="bg-gray-900 rounded-3xl p-6 text-white shadow-xl">
          <h3 className="text-sm font-bold mb-4 flex items-center gap-2">
            <span className="text-red-500 animate-pulse">●</span> Radar de Alertas
          </h3>
          <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
            {alerts.slice(0, 5).map((alert, i) => (
              <div key={i} className="border-l-2 border-red-500 pl-3 py-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-[10px] px-1.5 py-0.5 rounded uppercase font-bold ${getLevelBadge(alert.level)}`}>
                    {alert.level}
                  </span>
                  <span className="text-[10px] text-gray-400 font-mono">{alert.type}</span>
                </div>
                <p className="text-xs font-medium text-gray-200">{alert.message}</p>
                {alert.mitigation && <p className="text-[10px] text-gray-500 mt-1 italic">Miti: {alert.mitigation}</p>}
              </div>
            ))}
            {alerts.length === 0 && <p className="text-xs text-gray-500 italic">Nenhum alerta crítico ativo.</p>}
          </div>
        </div>
      </div>

      {/* Coluna 2 & 3: Ações Estratégicas Recomendadas */}
      <div className="lg:col-span-2">
        <div className="bg-white border border-gray-100 rounded-3xl p-6 shadow-sm h-full">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-gray-800">🎯 Recomendações Estratégicas</h3>
            <span className="text-xs bg-violet-100 text-violet-700 font-bold px-3 py-1 rounded-full">StrategicActionsEngine V8</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {actions.map((action, i) => (
              <div key={i} className="group border border-gray-50 bg-gray-50/30 rounded-2xl p-4 hover:border-violet-200 hover:bg-violet-50/20 transition-all">
                <div className="flex items-start justify-between mb-2">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    (action.priority === 'High' || (action.urgency && action.urgency >= 4)) ? 'bg-red-100 text-red-600' : 
                    (action.priority === 'Medium' || (action.urgency && action.urgency === 3)) ? 'bg-amber-100 text-amber-600' : 'bg-blue-100 text-blue-600'
                  }`}>
                    {action.priority || `${action.urgency}/5`} Priority
                  </span>
                  <span className="text-[10px] text-gray-400 font-mono uppercase">{action.category || action.action_type}</span>
                </div>
                <h4 className="text-sm font-bold text-gray-800 mb-1 group-hover:text-violet-700 transition-colors">{action.title}</h4>
                <p className="text-xs text-gray-500 mb-3 line-clamp-2">{action.description || (action.playbook && action.playbook[0])}</p>
                <div className="flex flex-wrap gap-1">
                  {(action.impact_area || action.channels || []).map((area, j) => (
                    <span key={j} className="text-[9px] bg-white border border-gray-100 px-1.5 py-0.5 rounded text-gray-400">
                      #{area}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
