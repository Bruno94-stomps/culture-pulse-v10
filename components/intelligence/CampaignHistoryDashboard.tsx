"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL } from "@/lib/fastapi";

interface CampaignHistoryItem {
  id?: string;
  brand_name: string;
  segment: string;
  campaign_text: string;
  match_score: number;
  authenticity_score: number;
  timestamp: string;
  risks: string[];
}

export default function CampaignHistoryDashboard() {
  const [history, setHistory] = useState<CampaignHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v8/analysis/history?limit=20`, {
            headers: { "Authorization": "Bearer cp_executive_2025_premium" }
        });
        const data = await response.json();
        setHistory(data.analyses || []);
      } catch (error) {
        console.error("Erro ao carregar histórico:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  if (loading) return <div className="animate-pulse flex space-x-4 p-10"><div className="flex-1 space-y-6 py-1"><div className="h-2 bg-slate-200 rounded"></div></div></div>;

  return (
    <div className="bg-white rounded-3xl border border-gray-100 shadow-xl overflow-hidden">
      <div className="p-6 border-b border-gray-50 flex justify-between items-center bg-gray-50/30">
        <div>
          <h2 className="text-xl font-black text-gray-900 leading-tight">Histórico de Campanhas</h2>
          <p className="text-[10px] font-black text-violet-600 uppercase tracking-widest mt-1">Audit Log Cultural V9.1</p>
        </div>
        <div className="bg-violet-100 px-3 py-1 rounded-full">
           <span className="text-xs font-bold text-violet-700">{history.length} ANÁLISES</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50/50">
              <th className="p-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">Data</th>
              <th className="p-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">Marca / Segmento</th>
              <th className="p-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">Match Score</th>
              <th className="p-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">Status de Risco</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {history.length > 0 ? history.map((item, idx) => (
              <tr key={idx} className="hover:bg-violet-50/30 transition-colors">
                <td className="p-4 text-xs text-gray-500 font-medium">
                  {new Date(item.timestamp).toLocaleDateString("pt-BR")}
                </td>
                <td className="p-4">
                  <div className="flex flex-col">
                    <span className="text-sm font-bold text-gray-900">{item.brand_name}</span>
                    <span className="text-[10px] text-gray-400 font-medium italic">{item.segment}</span>
                  </div>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <div className="w-12 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${item.match_score > 0.7 ? 'bg-emerald-500' : 'bg-amber-500'}`} 
                        style={{ width: `${item.match_score * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-bold text-gray-700">{(item.match_score * 100).toFixed(0)}%</span>
                  </div>
                </td>
                <td className="p-4">
                   <div className="flex flex-wrap gap-1">
                      {item.risks && item.risks.length > 0 ? (
                        <span className="px-2 py-0.5 bg-red-100 text-red-600 rounded-lg text-[9px] font-bold uppercase">
                          {item.risks.length} ALERTAS
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 bg-emerald-100 text-emerald-600 rounded-lg text-[9px] font-bold uppercase">
                          SAFE
                        </span>
                      )}
                   </div>
                </td>
              </tr>
            )) : (
              <tr>
                <td colSpan={4} className="p-10 text-center text-sm text-gray-400 italic">
                  Nenhuma campanha analisada recentemente.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
