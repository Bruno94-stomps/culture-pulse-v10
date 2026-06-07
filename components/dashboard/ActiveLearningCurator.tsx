"use client";

import { useState, useEffect } from "react";
import { Check, X, Info, Zap, Brain, MessageSquare, AlertCircle } from "lucide-react";

interface ActiveLearningStats {
  engine: string;
  version: string;
  total_feedback: number;
  total_queries: number;
  status_distribution: {
    validated: number;
    rejected: number;
    uncertain: number;
    needs_review: number;
  };
  avg_relevance: number;
  avg_uncertainty: number;
}

interface RankedQuery {
  query: string;
  relevance: number;
  uncertainty: number;
  feedback_count: number;
  status: string;
  priority: number;
}

import { FASTAPI_BASE_URL } from "@/lib/fastapi";

export default function ActiveLearningCurator() {
  const [uncertainQueries, setUncertainQueries] = useState<RankedQuery[]>([]);
  const [stats, setStats] = useState<ActiveLearningStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [feedbackLoading, setFeedbackLoading] = useState<string | null>(null);

  const API_BASE = `${FASTAPI_BASE_URL}/api/v8/active-learning`;

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statsRes, uncertainRes] = await Promise.all([
        fetch(`${API_BASE}/stats`),
        fetch(`${API_BASE}/uncertain?top_k=5`)
      ]);

      const statsData = await statsRes.json();
      const uncertainData = await uncertainRes.json();

      if (statsData.status === "success") setStats(statsData.data);
      if (uncertainData.status === "success") setUncertainQueries(uncertainData.data);
    } catch (error) {
      console.error("Erro ao carregar dados do Active Learning:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const submitFeedback = async (query: string, relevant: boolean) => {
    try {
      setFeedbackLoading(query);
      const response = await fetch(`${API_BASE}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          relevant,
          confidence: 1.0,
          source: "analyst",
          notes: "Feedback manual via Dashboard Next.js"
        })
      });

      if (response.ok) {
        // Remove da lista local e atualiza stats
        setUncertainQueries(prev => prev.filter(q => q.query !== query));
        fetchData();
      }
    } catch (error) {
      console.error("Erro ao enviar feedback:", error);
    } finally {
      setFeedbackLoading(null);
    }
  };

  if (loading && !stats) {
    return (
      <div className="bg-white rounded-xl border border-gray-100 p-8 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-600 mx-auto"></div>
        <p className="text-gray-500 text-sm mt-4">Carregando inteligência de curadoria...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Header */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-violet-50 to-white p-4 rounded-xl border border-violet-100">
          <div className="flex items-center gap-2 text-violet-700 mb-1">
            <Brain size={16} />
            <span className="text-xs font-semibold uppercase tracking-wider">Treinamento</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{stats?.total_feedback || 0}</p>
          <p className="text-xs text-gray-500">Feedbacks coletados</p>
        </div>
        
        <div className="bg-gradient-to-br from-blue-50 to-white p-4 rounded-xl border border-blue-100">
          <div className="flex items-center gap-2 text-blue-700 mb-1">
            <Zap size={16} />
            <span className="text-xs font-semibold uppercase tracking-wider">Incerteza Média</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{((stats?.avg_uncertainty || 0) * 100).toFixed(1)}%</p>
          <p className="text-xs text-gray-500">Necessidade de revisão</p>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-white p-4 rounded-xl border border-green-100">
          <div className="flex items-center gap-2 text-green-700 mb-1">
            <Check size={16} />
            <span className="text-xs font-semibold uppercase tracking-wider">Termos Validados</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{stats?.status_distribution.validated || 0}</p>
          <p className="text-xs text-gray-500">Filtros de confiança</p>
        </div>
      </div>

      {/* Curation Queue */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-50 flex items-center justify-between bg-gray-50/50">
          <div className="flex items-center gap-2">
            <MessageSquare size={18} className="text-gray-400" />
            <h3 className="font-semibold text-gray-700">Fila de Curadoria Cultural</h3>
          </div>
          <span className="text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-bold uppercase">
            Human-in-the-loop
          </span>
        </div>

        <div className="divide-y divide-gray-50">
          {uncertainQueries.length > 0 ? (
            uncertainQueries.map((q) => (
              <div key={q.query} className="p-4 flex items-center justify-between hover:bg-gray-50/30 transition">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">{q.query}</span>
                    <span className="text-[10px] bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">
                      Incerteza: {(q.uncertainty * 100).toFixed(0)}%
                    </span>
                  </div>
                  <p className="text-xs text-gray-400">
                    A IA detectou este termo mas precisa confirmar se ele é culturalmente relevante para o seu nicho.
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => submitFeedback(q.query, false)}
                    disabled={feedbackLoading === q.query}
                    className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition disabled:opacity-50"
                    title="Marcar como Irrelevante (Ruído)"
                  >
                    <X size={20} />
                  </button>
                  <button
                    onClick={() => submitFeedback(q.query, true)}
                    disabled={feedbackLoading === q.query}
                    className="p-2 text-green-600 bg-green-50 hover:bg-green-100 rounded-lg transition disabled:opacity-50 flex items-center gap-2"
                  >
                    <Check size={20} />
                    <span className="text-xs font-bold px-1">APROVAR</span>
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="p-12 text-center">
              <div className="bg-gray-50 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
                <Check className="text-gray-300" />
              </div>
              <p className="text-gray-500 text-sm">Fila limpa! A IA está operando com confiança.</p>
              <button 
                onClick={fetchData}
                className="mt-4 text-xs text-violet-600 font-medium hover:underline"
              >
                Checar novos termos
              </button>
            </div>
          )}
        </div>

        <div className="p-3 bg-gray-50 border-t border-gray-50 flex items-center gap-2 text-[11px] text-gray-400 italic">
          <Info size={12} />
          Seu feedback ajuda a economizar créditos de API descartando termos irrelevantes.
        </div>
      </div>

      {/* Import Assistant Card */}
      <div className="bg-amber-50 border border-amber-100 rounded-xl p-4 flex items-start gap-3">
        <div className="p-2 bg-amber-100 rounded-lg text-amber-700">
          <AlertCircle size={20} />
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-bold text-amber-900">Treinamento Automático Disponível</h4>
          <p className="text-xs text-amber-800 mt-1">
            Você pode importar o histórico do Query Tracker para ensinar a IA automaticamente com base no que já trouxe resultados no passado.
          </p>
          <button 
            className="mt-3 text-xs bg-amber-600 text-white px-3 py-1.5 rounded-lg font-bold hover:bg-amber-700 transition"
            onClick={async () => {
              const res = await fetch(`${API_BASE}/import-tracker`, { method: "POST", body: JSON.stringify({ limit: 100 }) });
              if (res.ok) fetchData();
            }}
          >
            IMPORTAR HISTÓRICO
          </button>
        </div>
      </div>
    </div>
  );
}
