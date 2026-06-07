"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { API_BASE_URL } from "@/lib/fastapi";
import { createClient } from "@/lib/supabase/client";

type Plan = "free" | "pro" | "executive" | "enterprise";
const PLAN_ORDER: Record<Plan, number> = { free: 0, pro: 1, executive: 2, enterprise: 3 };

interface PlanConfig {
  label: string;
  data_lag_hours: number;
  [key: string]: any;
}

interface Props {
  required:    Plan;
  current:     Plan;
  children:    React.ReactNode;
  /** Se true, renderiza um banner no lugar do conteúdo bloqueado */
  showBanner?: boolean;
  /**
   * Se true, ignora a verificação de plano e sempre mostra o conteúdo.
   * Usado no modo demo para exibir todas as funcionalidades.
   */
  forceOpen?:  boolean;
}

/**
 * PlanGate — bloqueia conteúdo se o plano atual não atinge o requerido.
 * Sincronizado com Backend V9.9 (Redis + PlanConfig)
 */
export default function PlanGate({ required, current, children, showBanner = true, forceOpen = false }: Props) {
  const [dynamicTiers, setDynamicTiers] = useState<Record<Plan, PlanConfig> | null>(null);
  const [authenticatedTier, setAuthenticatedTier] = useState<Plan | null>(null);
  const [planFallback, setPlanFallback] = useState(false);

  // Busca as definições reais do Backend V9.9 (Single Source of Truth)
  useEffect(() => {
    fetch(`${API_BASE_URL}/plans`)
      .then(res => res.json())
      .then(data => {
        if (data.tiers) setDynamicTiers(data.tiers);
      })
      .catch(err => console.error("Falha ao sincronizar PlanGate com Backend:", err));
  }, []);

  // Busca o plano autenticado do usuário logado
  useEffect(() => {
    async function fetchMyPlan() {
      try {
        const supabase = createClient();
        const {
          data: { session },
        } = await supabase.auth.getSession();

        const token = session?.access_token;
        if (!token) {
          setPlanFallback(true);
          return;
        }

        const response = await fetch(`${API_BASE_URL}/plans/my-plan`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          setPlanFallback(true);
          return;
        }

        const data = await response.json();
        if (data?.tier) {
          setAuthenticatedTier(data.tier as Plan);
        } else {
          setPlanFallback(true);
        }
      } catch (err) {
        console.error("Falha ao carregar plano autenticado:", err);
        setPlanFallback(true);
      }
    }

    fetchMyPlan();
  }, []);

  const effectiveCurrent = authenticatedTier ?? current;
  const isDemoMode = forceOpen || process.env.NEXT_PUBLIC_DEMO_MODE === "true";
  const allowed = isDemoMode || PLAN_ORDER[effectiveCurrent] >= PLAN_ORDER[required];

  if (allowed) {
    return (
      <>
        {planFallback && !isDemoMode && (
          <div className="mb-4 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-700 text-center">
            Não foi possível confirmar seu plano em tempo real, então estamos usando um fallback temporário. Se o problema persistir, atualize a página ou contate o suporte.
          </div>
        )}
        {children}
      </>
    );
  }

  if (!showBanner) return null;

  const PLAN_LABELS: Record<Plan, string> | null = dynamicTiers
    ? {
        free: dynamicTiers.free.label,
        pro: dynamicTiers.pro.label,
        executive: dynamicTiers.executive.label,
        enterprise: dynamicTiers.enterprise.label,
      }
    : null;

  const requiredLabel = PLAN_LABELS?.[required] ?? required.toUpperCase();
  const currentLabel = PLAN_LABELS?.[effectiveCurrent] ?? effectiveCurrent.toUpperCase();
  const lagHours = dynamicTiers ? dynamicTiers[required]?.data_lag_hours : undefined;

  return (
    <div className="relative rounded-2xl border-2 border-dashed border-amber-300 bg-amber-50 p-6 flex flex-col items-center gap-3 text-center min-h-[180px] justify-center overflow-hidden">
      {/* Blur overlay */}
      <div className="absolute inset-0 backdrop-blur-[2px] bg-white/30 rounded-2xl" />

      <div className="relative z-10 flex flex-col items-center gap-3">
        <div>
          <p className="font-bold text-gray-800 text-base">
            Disponível no plano{" "}
            <span className="text-violet-700">{requiredLabel}</span>
          </p>
          
          {/* V9.9: Justificativa Técnica baseada no Redis (Lag/TTL) */}
          {lagHours === 0 && (
            <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 bg-amber-100 text-amber-700 text-[11px] font-bold rounded-full uppercase tracking-wider">
              <span>⚡ Requisito: Tempo Real</span>
            </div>
          )}

          <p className="text-gray-500 text-sm mt-2">
            Seu plano atual é <b>{currentLabel}</b>. Faça upgrade para desbloquear.
          </p>
          {planFallback && !isDemoMode && (
            <p className="text-xs text-gray-500 mt-1">
              Usando fallback de plano. Verifique se o backend `/plans/my-plan` está acessível.
            </p>
          )}
        </div>
        <Link
          href={`/dashboard/upgrade?required=${required}`}
          className="px-5 py-2 bg-violet-700 text-white font-semibold rounded-lg hover:bg-violet-800 transition text-sm"
        >
          Fazer upgrade →
        </Link>
      </div>
    </div>
  );
}
