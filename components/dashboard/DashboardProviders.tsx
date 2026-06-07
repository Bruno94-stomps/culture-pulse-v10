"use client";

import { KeywordProvider } from "@/contexts/KeywordContext";
import type { ReactNode } from "react";

export default function DashboardProviders({ children }: { children: ReactNode }) {
  return <KeywordProvider>{children}</KeywordProvider>;
}
