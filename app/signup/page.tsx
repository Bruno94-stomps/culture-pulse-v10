"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default function SignupPage() {
  const router = useRouter();
  const supabase = createClient();

  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [name, setName]         = useState("");
  const [plan, setPlan]         = useState<"free" | "pro">("free");
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState<string | null>(null);
  const [success, setSuccess]   = useState(false);

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { full_name: name, plan },
        emailRedirectTo: `${location.origin}/auth/callback`,
      },
    });

    if (error) {
      setError(error.message);
      setLoading(false);
    } else {
      setSuccess(true);
    }
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-gray-900 rounded-2xl p-8 text-center space-y-4">
          <div className="text-5xl">📩</div>
          <h2 className="text-2xl font-bold text-white">Confirme seu e-mail</h2>
          <p className="text-gray-400">
            Enviamos um link de confirmação para <strong className="text-white">{email}</strong>.
            Clique nele para ativar sua conta no plano <span className="text-violet-400 capitalize">{plan}</span>.
          </p>
          <Link href="/login" className="block mt-4 text-violet-400 hover:text-violet-300 text-sm">
            Ir para o login →
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Logo */}
        <div className="text-center">
          <span className="text-4xl">🧠</span>
          <h1 className="mt-2 text-2xl font-bold text-white">Culture Pulse</h1>
          <p className="text-gray-400 text-sm mt-1">Inteligência cultural em tempo real</p>
        </div>

        {/* Seleção de plano */}
        <div className="grid grid-cols-2 gap-3">
          {(["free", "pro"] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPlan(p)}
              className={`rounded-xl border p-4 text-left transition-all ${
                plan === p
                  ? "border-violet-500 bg-violet-900/30"
                  : "border-gray-700 bg-gray-900 hover:border-gray-600"
              }`}
            >
              <div className={`text-xs font-semibold uppercase tracking-wide mb-1 ${
                p === "pro" ? "text-violet-400" : "text-gray-400"
              }`}>
                {p === "free" ? "Grátis" : "Pro"}
              </div>
              <div className="text-white font-bold">
                {p === "free" ? "R$ 0/mês" : "R$ 297/mês"}
              </div>
              <div className="text-gray-400 text-xs mt-1">
                {p === "free"
                  ? "3 círculos, 60s delay"
                  : "16 círculos, tempo real"}
              </div>
            </button>
          ))}
        </div>

        {/* Form */}
        <form onSubmit={handleSignup} className="bg-gray-900 rounded-2xl p-8 space-y-5">
          <h2 className="text-xl font-semibold text-white">Criar conta</h2>

          {error && (
            <div className="bg-red-900/40 border border-red-700 rounded-lg p-3 text-red-300 text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm text-gray-400 mb-1.5">Nome completo</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-violet-500 transition"
              placeholder="Seu nome"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1.5">E-mail</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-violet-500 transition"
              placeholder="voce@empresa.com.br"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1.5">Senha</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-violet-500 transition"
              placeholder="Mínimo 8 caracteres"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors"
          >
            {loading ? "Criando conta..." : "Criar conta gratuita"}
          </button>

          <p className="text-center text-gray-500 text-sm">
            Já tem conta?{" "}
            <Link href="/login" className="text-violet-400 hover:text-violet-300">
              Entrar
            </Link>
          </p>
        </form>

        <p className="text-center text-gray-600 text-xs">
          Ao criar uma conta você concorda com nossos{" "}
          <a href="#" className="text-gray-400 hover:text-gray-300">Termos de Uso</a>
          {" "}e{" "}
          <a href="#" className="text-gray-400 hover:text-gray-300">Política de Privacidade</a>.
        </p>
      </div>
    </div>
  );
}
