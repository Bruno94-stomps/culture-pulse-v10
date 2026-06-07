"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

interface Props {
  projectId: string;
  status: string;
}

export default function AnalyzeButton({ projectId, status }: Props) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isRunning = status === "collecting" || status === "analyzing";

  async function handleAnalyze() {
    setLoading(true);
    setError(null);

    try {
      // 1) Fetch project details
      const projRes = await fetch(`/api/projects/${projectId}`);
      if (!projRes.ok) throw new Error("Falha ao carregar projeto");
      const projJson = await projRes.json();
      const project = projJson.data ?? projJson;

      // 2) Trigger server-side analysis flow for the project
      const triggerRes = await fetch(`/api/projects/${projectId}`, {
        method: "POST",
      });

      if (!triggerRes.ok) {
        const payload = await triggerRes.json();
        throw new Error(payload.error || "Falha ao iniciar a análise do projeto");
      }

      await router.push(`/dashboard/insights?projectId=${projectId}`);
    } catch (err: any) {
      setError(err.message ?? "Erro ao analisar");
      // Revert status
      await fetch(`/api/projects/${projectId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "error" }),
      });
    } finally {
      setLoading(false);
    }
  }

  if (status === "archived") return null;

  return (
    <div className="flex flex-col items-end gap-1">
      <button
        onClick={handleAnalyze}
        disabled={loading || isRunning}
        className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${
          loading || isRunning
            ? "bg-gray-100 text-gray-400 cursor-not-allowed"
            : "bg-violet-600 text-white hover:bg-violet-700 shadow-sm"
        }`}
      >
        {loading
          ? "⏳ Analisando…"
          : isRunning
          ? "🔄 Em andamento…"
          : status === "ready"
          ? "🔁 Re-analisar"
          : "🚀 Analisar Agora"}
      </button>
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
