"use client";

import { CheckCircle2, AlertTriangle, Layers } from "lucide-react";

interface ComparisonCardProps {
  segment: string;
  brandScore: number;
  audienceScore: number;
}

export default function TwinComparisonCard({ segment, brandScore, audienceScore }: ComparisonCardProps) {
  const diff = Math.abs(brandScore - audienceScore);
  const isMatch = diff < 0.2;
  const isAlert = diff > 0.5;

  return (
    <div className={`p-4 rounded-2xl border transition-all ${
      isMatch ? "bg-emerald-50 border-emerald-100" : 
      isAlert ? "bg-amber-50 border-amber-100 ring-2 ring-amber-100/50" : 
      "bg-white border-gray-100"
    }`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] font-black uppercase tracking-widest text-gray-400">{segment.replace(/_/g, " ")}</span>
        {isMatch ? (
          <CheckCircle2 size={16} className="text-emerald-500" />
        ) : isAlert ? (
          <AlertTriangle size={16} className="text-amber-500" />
        ) : (
          <Layers size={16} className="text-gray-300" />
        )}
      </div>

      <div className="flex items-end gap-4">
        <div className="flex-1">
          <div className="flex justify-between text-[10px] mb-1">
            <span className="font-bold text-gray-500">Match Rate</span>
            <span className={`font-black ${isMatch ? "text-emerald-700" : isAlert ? "text-amber-700" : "text-gray-700"}`}>
              {((1 - diff) * 100).toFixed(0)}%
            </span>
          </div>
          <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-1000 ${
                isMatch ? "bg-emerald-500" : isAlert ? "bg-amber-500" : "bg-violet-400"
              }`}
              style={{ width: `${(1 - diff) * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
