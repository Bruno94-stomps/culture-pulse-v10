"use client";

import { createContext, useContext, useState, useMemo } from "react";
import type { ExportData } from "@/lib/utils/pdf-export";

interface ExportContextValue {
  exportData: ExportData | null;
  setExportData: (data: ExportData | null) => void;
}

const ExportContext = createContext<ExportContextValue | undefined>(undefined);

export function ExportProvider({ children }: { children: React.ReactNode }) {
  const [exportData, setExportData] = useState<ExportData | null>(null);
  const value = useMemo(() => ({ exportData, setExportData }), [exportData]);

  return <ExportContext.Provider value={value}>{children}</ExportContext.Provider>;
}

export function useExportDataContext() {
  const context = useContext(ExportContext);
  if (!context) {
    throw new Error("useExportDataContext must be used within ExportProvider");
  }
  return context;
}
