"use client";

import { ShieldCheck, AlertCircle, TrendingUp, TrendingDown } from "lucide-react";

interface CulturalShieldProps {
  score: number;
  overall_risk: "low" | "medium" | "high" | "critical";
  alerts: Array<{ id: string; message: string; severity: "info" | "warning" | "error" }>;
}

export default function CulturalShield({ score, overall_risk, alerts }: CulturalShieldProps) {
  const isCritical = overall_risk === "critical" || overall_risk === "high";

  return (
    <div className={`relative px-4 py-4 rounded-2xl shadow-xl border-t-4 transition-all overflow-hidden ${
      isCritical 
        ? "bg-red-50 border-red-500 shadow-red-200/50" 
        : "bg-emerald-50 border-emerald-500 shadow-emerald-200/50"
    }`}>
      {/* Background Decorator */}
      <div className={`absolute -right-4 -top-4 opacity-5 pointer-events-none scale-150 rotate-12 transition ${
        isCritical ? "text-red-900" : "text-emerald-900"
      }`}>
        <ShieldCheck size={120} />
      </div>

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className={`p-2 rounded-xl text-white ${isCritical ? "bg-red-500" : "bg-emerald-500"}`}>
            <ShieldCheck size={20} />
          </div>
          <div>
            <h3 className={`font-extrabold text-sm uppercase tracking-tighter ${
              isCritical ? "text-red-900" : "text-emerald-900"
            }`}>Cultural Shield</h3>
            <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest opacity-70">
              V9.1 Protection Active
            </p>
          </div>
        </div>

        <div className={`px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider transition ${
          isCritical ? "bg-red-100 text-red-700 shadow-sm border border-red-200" : "bg-emerald-100 text-emerald-700 shadow-sm border border-emerald-200 shadow-emerald-100"
        }`}>
          {overall_risk} risk
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-white/50 border border-white p-3 rounded-xl backdrop-blur-md">
          <span className="text-[10px] uppercase font-bold text-gray-400 block mb-1">CVI Score</span>
          <div className="flex items-end gap-1.5">
            <span className={`text-2xl font-black ${isCritical ? "text-red-600" : "text-emerald-600"}`}>
              {score.toFixed(0)}
            </span>
            {score > 50 ? (
              <TrendingUp size={16} className="text-emerald-500 mb-1" />
            ) : (
              <TrendingDown size={16} className="text-red-500 mb-1" />
            )}
          </div>
        </div>
        
        <div className="bg-white/50 border border-white p-3 rounded-xl backdrop-blur-md">
          <span className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Active Alerts</span>
          <span className={`text-2xl font-black ${alerts.length > 0 ? "text-amber-600" : "text-gray-300"}`}>
            {alerts.length.toString().padStart(2, '0')}
          </span>
        </div>
      </div>

      {alerts.length > 0 ? (
        <div className="space-y-1.5 animate-in fade-in slide-in-from-bottom-2">
          {alerts.map((alert) => (
            <div 
              key={alert.id}
              className={`flex items-start gap-2 p-2 rounded-lg text-[10px] leading-tight font-bold border transition ${
                alert.severity === "error" 
                  ? "bg-red-100/50 border-red-200 text-red-900" 
                  : "bg-amber-100/50 border-amber-200 text-amber-900"
              }`}
            >
              <AlertCircle size={14} className="shrink-0 mt-0.5" />
              <span>{alert.message}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-3 bg-white/30 border border-dashed border-emerald-400/30 rounded-xl text-center">
          <p className="text-[10px] text-emerald-700 font-bold opacity-60">
            Nenhuma dissonância cultural detectada
          </p>
        </div>
      )}
    </div>
  );
}
