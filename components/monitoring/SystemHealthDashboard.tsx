"use client";

import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Zap, 
  BarChart3, 
  AlertTriangle, 
  CheckCircle2, 
  Clock,
  RefreshCw,
  Search,
  Globe,
  Database
} from 'lucide-react';

interface APIStatus {
  name: string;
  status: 'online' | 'degraded' | 'offline';
  latency: number;
  successRate: number;
  requests: number;
}

interface DriftMetric {
  category: string;
  drift_score: number;
  status: 'stable' | 'warning' | 'drifted';
  last_check: string;
}

import { FASTAPI_BASE_URL } from "@/lib/fastapi";

export default function SystemHealthDashboard() {
  const [apiStatuses, setApiStatuses] = useState<APIStatus[]>([
    { name: 'YouTube API', status: 'online', latency: 145, successRate: 99.8, requests: 1250 },
    { name: 'Reddit API', status: 'online', latency: 320, successRate: 98.5, requests: 840 },
    { name: 'Spotify SDK', status: 'online', latency: 85, successRate: 99.9, requests: 2100 },
    { name: 'NewsAPI', status: 'degraded', latency: 850, successRate: 92.1, requests: 450 },
    { name: 'Instagram Graph', status: 'offline', latency: 0, successRate: 0, requests: 0 },
  ]);

  const [drifts, setDrifts] = useState<DriftMetric[]>([
    { category: 'Linguagem Urbana', drift_score: 0.12, status: 'stable', last_check: '2m atrás' },
    { category: 'Cultura K-Pop', drift_score: 0.45, status: 'warning', last_check: '5m atrás' },
    { category: 'Política BR', drift_score: 0.78, status: 'drifted', last_check: '1m atrás' },
  ]);

  const [isRefreshing, setIsRefreshing] = useState(false);

  const refreshData = async () => {
    setIsRefreshing(true);
    try {
      const response = await fetch(`${FASTAPI_BASE_URL}/api/v8/health/detailed`);
      const data = await response.json();
      
      if (data.api_statuses) {
        setApiStatuses(data.api_statuses);
      }
      if (data.drifts) {
        setDrifts(data.drifts);
      }
    } catch (error) {
      console.error("Erro ao buscar saúde do sistema:", error);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    refreshData();
    const interval = setInterval(refreshData, 30000); // Auto-refresh a cada 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Activity className="text-violet-500 w-5 h-5" />
            Saúde do Sistema em Tempo Real
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Monitoramento v9.1: Latência, Drift Semântico e Conectividade
          </p>
        </div>
        <button 
          onClick={refreshData}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-3 py-1.5 bg-violet-600 hover:bg-violet-700 text-white rounded-md text-sm font-medium transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          Atualizar
        </button>
      </div>

      {/* Grid de Métricas Rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <HealthCard 
          title="Uptime Global" 
          value="99.98%" 
          sub="30 dias seguidos" 
          icon={<Zap className="w-5 h-5 text-amber-500" />} 
        />
        <HealthCard 
          title="Latência Média" 
          value="182ms" 
          sub="-12ms vs ontem" 
          icon={<Clock className="w-5 h-5 text-blue-500" />} 
        />
        <HealthCard 
          title="Drift Detectado" 
          value="Médio" 
          sub="3 categorias alertas" 
          icon={<RefreshCw className="w-5 h-5 text-violet-500" />} 
        />
        <HealthCard 
          title="Volume de Sinais" 
          value="24.5k" 
          sub="+5% este ciclo" 
          icon={<Database className="w-5 h-5 text-emerald-500" />} 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Status das APIs */}
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <Globe className="w-4 h-4 text-violet-500" />
              API Connectors (P2P Monitoring)
            </h3>
            <span className="text-xs font-medium text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 px-2 py-0.5 rounded-full">
              4 Online
            </span>
          </div>
          <div className="divide-y divide-gray-100 dark:divide-gray-700">
            {apiStatuses.map((api) => (
              <div key={api.name} className="px-5 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${
                    api.status === 'online' ? 'bg-emerald-500' : 
                    api.status === 'degraded' ? 'bg-amber-500' : 'bg-red-500'
                  }`} />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-200">{api.name}</span>
                </div>
                <div className="flex items-center gap-8">
                  <div className="text-right">
                    <p className="text-xs text-gray-500">Latência</p>
                    <p className="text-sm font-semibold">{api.status === 'offline' ? '--' : `${api.latency}ms`}</p>
                  </div>
                  <div className="text-right w-16">
                    <p className="text-xs text-gray-500">Sucesso</p>
                    <p className={`text-sm font-semibold ${api.successRate < 95 ? 'text-amber-500' : 'text-gray-700 dark:text-gray-200'}`}>
                      {api.status === 'offline' ? '0%' : `${api.successRate}%`}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Drift Semântico */}
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-violet-500" />
              Semantic Drift (IA Monitoring)
            </h3>
          </div>
          <div className="p-5 space-y-4">
            {drifts.map((d) => (
              <div key={d.category} className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="font-medium text-gray-600 dark:text-gray-400">{d.category}</span>
                  <span className={
                    d.status === 'stable' ? 'text-emerald-500' : 
                    d.status === 'warning' ? 'text-amber-500' : 'text-red-500'
                  }>
                    {d.status.toUpperCase()}
                  </span>
                </div>
                <div className="h-2 w-full bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${
                      d.status === 'stable' ? 'bg-emerald-500' : 
                      d.status === 'warning' ? 'bg-amber-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${d.drift_score * 100}%` }}
                  />
                </div>
              </div>
            ))}
            <div className="mt-4 p-3 bg-violet-50 dark:bg-violet-900/20 rounded-lg text-xs text-violet-700 dark:text-violet-300">
              <div className="flex gap-2">
                <Search className="w-4 h-4 shrink-0" />
                <p>O motor detectou que o termo "Política BR" está convergindo para novos contextos semânticos no Twitter/X.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function HealthCard({ title, value, sub, icon }: { title: string, value: string, sub: string, icon: React.ReactNode }) {
  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 p-5 rounded-xl shadow-sm">
      <div className="flex items-center gap-3 mb-2">
        {icon}
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{title}</span>
      </div>
      <div className="text-2xl font-bold text-gray-900 dark:text-white">{value}</div>
      <div className="text-xs text-emerald-500 font-medium">{sub}</div>
    </div>
  );
}
