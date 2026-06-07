"use client";

interface CircleTermo {
  termo: string;
  score: number;
  count: number;
}

interface Circle {
  name: string;
  categoria: string;
  icon: string;
  totalSignals: number;
  avgScore: number;
  maxScore: number;
  platforms: string[];
  topTermos: CircleTermo[];
}

const CATEGORIA_COLORS: Record<string, string> = {
  Entretenimento:  "from-violet-500 to-purple-600",
  Comportamento:   "from-blue-500 to-cyan-600",
  Consumo:         "from-amber-500 to-orange-600",
  Identidade:      "from-green-500 to-emerald-600",
  Espiritualidade: "from-pink-500 to-rose-600",
  Outros:          "from-gray-400 to-gray-500",
};

const PLATFORM_ICON: Record<string, string> = {
  youtube:   "▶️",
  reddit:    "💬",
  spotify:   "🎧",
  newsapi:   "📰",
  rss:       "📡",
  trends:    "📈",
  instagram: "📸",
  meetup:    "🤝",
  eventbrite:"🎟️",
};

export default function CircleCards({ circles }: { circles: Circle[] }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-700 mb-4">
        📋 Detalhes por Círculo
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {circles.map((c) => {
          const gradient =
            CATEGORIA_COLORS[c.categoria] ?? CATEGORIA_COLORS["Outros"];
          return (
            <div
              key={c.name}
              className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition"
            >
              {/* Header Bar */}
              <div className={`h-1.5 bg-gradient-to-r ${gradient}`} />

              <div className="p-4 space-y-3">
                {/* Title Row */}
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{c.icon}</span>
                  <div>
                    <h4 className="font-semibold text-gray-900 text-sm leading-tight">
                      {c.name}
                    </h4>
                    <span className="text-[11px] text-gray-400">
                      {c.categoria}
                    </span>
                  </div>
                </div>

                {/* Score + Signals Row */}
                <div className="flex items-center gap-4">
                  <div>
                    <p className="text-lg font-bold text-gray-900">
                      {(c.avgScore * 100).toFixed(1)}%
                    </p>
                    <p className="text-[10px] text-gray-400">Score médio</p>
                  </div>
                  <div>
                    <p className="text-lg font-bold text-gray-900">
                      {c.totalSignals}
                    </p>
                    <p className="text-[10px] text-gray-400">Sinais</p>
                  </div>
                  <div className="flex-1 flex justify-end gap-1">
                    {c.platforms.map((p) => (
                      <span key={p} title={p} className="text-sm">
                        {PLATFORM_ICON[p.toLowerCase()] ?? "•"}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full bg-gradient-to-r ${gradient} transition-all`}
                    style={{ width: `${Math.round(c.avgScore * 100)}%` }}
                  />
                </div>

                {/* Top Termos */}
                {c.topTermos.length > 0 && (
                  <div className="space-y-1.5 pt-1">
                    <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">
                      Top termos
                    </p>
                    {c.topTermos.map((t) => (
                      <div
                        key={t.termo}
                        className="flex items-center justify-between text-xs"
                      >
                        <span className="text-gray-700 truncate max-w-[55%]">
                          {t.termo}
                        </span>
                        <div className="flex items-center gap-2">
                          <span className="text-gray-400">{t.count}×</span>
                          <span className="font-mono font-medium text-gray-600">
                            {(t.score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
