import Link from "next/link";
import { getCurrentPlan } from "@/lib/plan";
import { API_BASE_URL } from "@/lib/fastapi";

const PLANS = [
  {
    key: "free",
    name: "Free",
    price: "R$ 0",
    period: "/mês",
    color: "border-gray-700",
    badge: "bg-gray-700 text-gray-300",
    cta: null,
    features: [
      "Histórico D+1 (Atraso 24h)",
      "3 círculos culturais",
      "Score cultural básico",
      "100 sinais/dia",
      "Dashboard simplificado",
    ],
    locked: [
      "Dados em Tempo Real",
      "Histórico de 7+ dias",
      "16 círculos completos",
      "Radar Alma Brasileira",
      "Mapa regional",
    ],
  },
  {
    key: "pro",
    name: "Pro",
    price: "R$ 297",
    period: "/mês",
    color: "border-violet-500",
    badge: "bg-violet-700 text-violet-100",
    cta: "https://buy.stripe.com/pro", // substituir pelo link real
    features: [
      "Dados em Tempo Real",
      "Histórico de 7 dias",
      "16 círculos culturais completos",
      "Radar Alma Brasileira completo",
      "Mapa de calor regional",
      "Exportação CSV/JSON",
    ],
    locked: [
      "Histórico de 30+ dias",
      "Dados brutos (raw_data)",
      "API ilimitada",
    ],
  },
  {
    key: "enterprise",
    name: "Enterprise",
    price: "Sob consulta",
    period: "",
    color: "border-amber-500",
    badge: "bg-amber-600 text-amber-100",
    cta: "mailto:enterprise@culturepulse.com.br",
    features: [
      "Real-time & Full History",
      "Histórico Ilimitado (90+ dias)",
      "Dados brutos completos",
      "API ilimitada",
      "Streaming 10s (near real-time)",
      "SLA 99,9% garantido",
      "Relatórios customizados",
    ],
    locked: [],
  },
] as const;

export default async function UpgradePage({
  searchParams,
}: {
  searchParams: { required?: string };
}) {
  const currentPlan = await getCurrentPlan();

  const requiredPlan = searchParams.required ?? null;

  return (
    <div className="min-h-screen bg-gray-950 py-16 px-4">
      <div className="max-w-5xl mx-auto space-y-10">
        {/* Header */}
        <div className="text-center space-y-3">
          {requiredPlan && (
            <div className="inline-flex items-center gap-2 bg-amber-900/30 border border-amber-700 rounded-full px-4 py-1.5 text-amber-300 text-sm">
              🔒 Esta funcionalidade requer o plano{" "}
              <span className="font-semibold capitalize">{requiredPlan}</span>
            </div>
          )}
          <h1 className="text-3xl md:text-4xl font-bold text-white">
            Escolha seu plano
          </h1>
          <p className="text-gray-400 max-w-lg mx-auto">
            Inteligência cultural brasileira em tempo real. Cancele quando quiser.
          </p>
        </div>

        {/* Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {PLANS.map((plan) => {
            const isCurrent = plan.key === currentPlan;
            const isHighlighted = plan.key === "pro";

            return (
              <div
                key={plan.key}
                className={`relative rounded-2xl border-2 p-6 space-y-6 ${plan.color} ${
                  isHighlighted ? "bg-violet-950/30" : "bg-gray-900"
                }`}
              >
                {isHighlighted && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-violet-600 text-white text-xs font-bold px-3 py-1 rounded-full">
                      MAIS POPULAR
                    </span>
                  </div>
                )}

                {/* Header do plano */}
                <div>
                  <span className={`text-xs font-bold uppercase tracking-widest px-2.5 py-1 rounded-full ${plan.badge}`}>
                    {plan.name}
                  </span>
                  <div className="mt-3">
                    <span className="text-3xl font-extrabold text-white">{plan.price}</span>
                    <span className="text-gray-400 text-sm ml-1">{plan.period}</span>
                  </div>
                </div>

                {/* Features incluídas */}
                <ul className="space-y-2.5">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-gray-200">
                      <span className="text-green-400 mt-0.5 shrink-0">✓</span>
                      {f}
                    </li>
                  ))}
                  {plan.locked.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-gray-600">
                      <span className="mt-0.5 shrink-0">✗</span>
                      {f}
                    </li>
                  ))}
                </ul>

                {/* CTA */}
                {isCurrent ? (
                  <div className="w-full text-center py-3 rounded-xl bg-gray-800 text-gray-400 text-sm font-medium">
                    Plano atual
                  </div>
                ) : plan.cta ? (
                  <a
                    href={plan.cta}
                    className={`block w-full text-center py-3 rounded-xl font-semibold transition-colors ${
                      plan.key === "enterprise"
                        ? "bg-amber-600 hover:bg-amber-500 text-white"
                        : "bg-violet-600 hover:bg-violet-500 text-white"
                    }`}
                  >
                    {plan.key === "enterprise" ? "Falar com vendas" : "Fazer upgrade"}
                  </a>
                ) : null}
              </div>
            );
          })}
        </div>

        {/* Voltar */}
        <div className="text-center">
          <Link
            href="/dashboard"
            className="text-gray-500 hover:text-gray-300 text-sm transition-colors"
          >
            ← Voltar ao dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
