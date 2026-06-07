import Link from "next/link";

/**
 * Landing page pública — apresenta os planos e CTA de login.
 */
export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-violet-950 via-violet-900 to-amber-900 text-white">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-6">
        <span className="text-2xl font-bold tracking-tight">
          Culture<span className="text-amber-400">Pulse</span>
        </span>
        <div className="flex gap-4">
          <Link
            href="/login"
            className="px-4 py-2 rounded-lg border border-white/20 hover:bg-white/10 transition"
          >
            Entrar
          </Link>
          <Link
            href="/signup"
            className="px-4 py-2 rounded-lg bg-amber-400 text-violet-950 font-semibold hover:bg-amber-300 transition"
          >
            Começar grátis
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="flex flex-col items-center text-center px-6 pt-24 pb-32 gap-8">
        <div className="px-3 py-1 rounded-full bg-amber-400/20 text-amber-300 text-sm font-medium">
          ⚡ Sinais culturais em tempo real
        </div>
        <h1 className="text-5xl md:text-7xl font-extrabold leading-tight max-w-4xl">
          Entenda o Brasil{" "}
          <span className="text-amber-400">antes da virada</span>
        </h1>
        <p className="text-xl text-white/70 max-w-2xl">
          16 círculos culturais · 8 fontes de dados · Streaming em tempo real.
          Detecte tendências culturais 6-12 meses antes do mainstream.
        </p>
        <div className="flex gap-4 flex-wrap justify-center">
          <Link
            href="/signup"
            className="px-8 py-4 bg-amber-400 text-violet-950 font-bold rounded-xl text-lg hover:bg-amber-300 transition"
          >
            Criar conta grátis
          </Link>
          <Link
            href="/onboarding?demo=true"
            className="px-8 py-4 border border-white/30 rounded-xl text-lg hover:bg-white/10 transition"
          >
            Ver demo →
          </Link>
        </div>
      </section>

      {/* Planos */}
      <section className="px-8 pb-24 max-w-5xl mx-auto grid md:grid-cols-3 gap-6">
        {[
          {
            plan: "Free",
            price: "R$0",
            features: ["3 círculos culturais", "Sinais básicos", "30 req/dia", "Dashboard limitado"],
            cta: "Começar grátis",
            href: "/signup?plan=free",
            highlight: false,
          },
          {
            plan: "Pro",
            price: "R$297/mês",
            features: ["16 círculos culturais", "Streaming em tempo real", "1.000 req/hora", "Mapa regional", "Exportação CSV"],
            cta: "Assinar Pro",
            href: "/signup?plan=pro",
            highlight: true,
          },
          {
            plan: "Enterprise",
            price: "Sob consulta",
            features: ["Tudo do Pro", "API sem limite", "Raw data acesso", "Suporte dedicado", "SLA 99.9%"],
            cta: "Falar com vendas",
            href: "/contato",
            highlight: false,
          },
        ].map((tier) => (
          <div
            key={tier.plan}
            className={`rounded-2xl p-6 flex flex-col gap-4 ${
              tier.highlight
                ? "bg-amber-400 text-violet-950 shadow-2xl scale-105"
                : "bg-white/10 text-white"
            }`}
          >
            <div>
              <p className="text-sm font-semibold uppercase opacity-70">{tier.plan}</p>
              <p className="text-3xl font-extrabold mt-1">{tier.price}</p>
            </div>
            <ul className="flex-1 space-y-2 text-sm">
              {tier.features.map((f) => (
                <li key={f} className="flex items-center gap-2">
                  <span>✓</span> {f}
                </li>
              ))}
            </ul>
            <Link
              href={tier.href}
              className={`mt-2 text-center py-3 rounded-xl font-bold transition ${
                tier.highlight
                  ? "bg-violet-950 text-amber-400 hover:bg-violet-900"
                  : "bg-white/20 hover:bg-white/30"
              }`}
            >
              {tier.cta}
            </Link>
          </div>
        ))}
      </section>
    </main>
  );
}
