"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { buildMockSignalsFromKeywords } from "@/lib/mock-data";
import { FASTAPI_BASE_URL } from "@/lib/fastapi";

const IS_DEMO = process.env.NEXT_PUBLIC_DEMO_MODE === "true";

// ─── Types ─────────────────────────────────────────────────────────────────────

export interface ActiveSignal {
  termo: string;
  momentum: number;
  sentiment: number;
  volume: number;
  plataforma: string;
  score?: number;
  circulo?: string;
  regiao?: string;
}

export interface KeywordProject {
  keywords: string[];
  brand: string;
  sector: string;
  periodDays: number;
}

interface KeywordContextValue {
  keywords: string[];
  brand: string;
  sector: string;
  periodDays: number;
  signals: ActiveSignal[];
  hasKeywords: boolean;
  signalsLoading: boolean;
  hydrated: boolean;
  setProject: (project: Partial<KeywordProject>) => void;
  clearProject: () => void;
}

// ─── Defaults ──────────────────────────────────────────────────────────────────

const STORAGE_KEY = "cp_project_v1";
const API_BASE = FASTAPI_BASE_URL;
const API_TOKEN = "cp_demo_2025_free_tier";

const DEFAULT_PROJECT: KeywordProject = {
  keywords: [],
  brand: "",
  sector: "",
  periodDays: 30,
};

const DEMO_PROJECT: KeywordProject = {
  keywords: ["funk", "sertanejo", "sustentabilidade", "ia generativa", "cultura indígena"],
  brand: "Demo Brand",
  sector: "Entretenimento",
  periodDays: 30,
};

// ─── Context ───────────────────────────────────────────────────────────────────

const KeywordContext = createContext<KeywordContextValue | null>(null);

export function KeywordProvider({ children }: { children: ReactNode }) {
  const [project, setProjectState] = useState<KeywordProject>(DEFAULT_PROJECT);
  const [signals, setSignals] = useState<ActiveSignal[]>([]);
  const [signalsLoading, setSignalsLoading] = useState(false);
  // hydrated: true after localStorage has been read — prevents premature empty-fetch
  const [hydrated, setHydrated] = useState(false);

  // Step 1 — rehydrate from localStorage once on mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<KeywordProject>;
        setProjectState((prev) => ({ ...prev, ...parsed }));
      }
    } catch {
      // ignore corrupt storage
    } finally {
      setHydrated(true);
    }
  }, []);

  // Step 2 — fetch real signals only AFTER hydration + when keywords change
  useEffect(() => {
    if (!hydrated) return;               // wait for localStorage read

    // ── DEMO MODE: use mock data instantly, no fetch needed ──
    // Falls back to DEMO_PROJECT keywords when user has none (direct URL access)
    if (IS_DEMO) {
      const kws = project.keywords.length > 0 ? project.keywords : DEMO_PROJECT.keywords;
      setSignals(buildMockSignalsFromKeywords(kws));
      return;
    }

    if (project.keywords.length === 0) {
      setSignals([]);
      return;
    }

    const controller = new AbortController();
    setSignalsLoading(true);

    const params = new URLSearchParams({
      keywords: project.keywords.join(","),
      period_days: String(project.periodDays),
      limit: "50",
    });

    fetch(`${API_BASE}/api/v8/signals/live?${params}`, {
      headers: { Authorization: `Bearer ${API_TOKEN}` },
      signal: controller.signal,
    })
      .then((r) => r.json())
      .then((d) => {
        const data: ActiveSignal[] = d?.data ?? [];
        if (data.length > 0) {
          setSignals(data);
        } else {
          // Fallback: one synthetic signal per keyword so UX never breaks
          setSignals(project.keywords.map((termo, i) => ({
            termo,
            momentum: 0.5 + i * 0.05,
            sentiment: 0.6,
            volume: 20,
            plataforma: ["YouTube", "Spotify", "Reddit", "Instagram", "NewsAPI"][i % 5],
          })));
        }
      })
      .catch((err) => {
        if (err.name === "AbortError") return;
        setSignals(project.keywords.map((termo, i) => ({
          termo,
          momentum: 0.5 + i * 0.05,
          sentiment: 0.6,
          volume: 20,
          plataforma: ["YouTube", "Spotify", "Reddit", "Instagram", "NewsAPI"][i % 5],
        })));
      })
      .finally(() => setSignalsLoading(false));

    return () => controller.abort();
  }, [hydrated, project.keywords, project.periodDays]);

  const setProject = useCallback((updates: Partial<KeywordProject>) => {
    setProjectState((prev) => {
      const next = { ...prev, ...updates };
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } catch {
        // ignore
      }
      return next;
    });
  }, []);

  const clearProject = useCallback(() => {
    setProjectState(DEFAULT_PROJECT);
    setSignals([]);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore
    }
  }, []);

  return (
    <KeywordContext.Provider
      value={{
        keywords: project.keywords,
        brand: project.brand,
        sector: project.sector,
        periodDays: project.periodDays,
        signals,
        hasKeywords: IS_DEMO ? true : project.keywords.length > 0,
        signalsLoading,
        hydrated,
        setProject,
        clearProject,
      }}
    >
      {children}
    </KeywordContext.Provider>
  );
}

// ─── Hook ──────────────────────────────────────────────────────────────────────

export function useKeywords(): KeywordContextValue {
  const ctx = useContext(KeywordContext);
  if (!ctx) throw new Error("useKeywords must be used inside <KeywordProvider>");
  return ctx;
}

// ─── Demo helper ───────────────────────────────────────────────────────────────

export { DEMO_PROJECT };

