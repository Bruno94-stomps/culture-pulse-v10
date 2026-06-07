"use client";

import { createContext, useContext, useMemo } from "react";
import type { User } from "@supabase/supabase-js";

export type Plan = "free" | "pro" | "executive" | "enterprise";

interface DashboardContextValue {
  user: User | null;
  plan: Plan;
}

const DashboardContext = createContext<DashboardContextValue | undefined>(undefined);

export function DashboardProvider({
  user,
  plan,
  children,
}: {
  user: User | null;
  plan: Plan;
  children: React.ReactNode;
}) {
  const value = useMemo(() => ({ user, plan }), [user, plan]);

  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
}

export function useDashboardContext() {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error("useDashboardContext must be used within DashboardProvider");
  }
  return context;
}
