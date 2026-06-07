"use client";

import { useEffect } from "react";
import { useExportDataContext } from "@/components/dashboard/ExportContext";
import type { ExportData } from "@/lib/utils/pdf-export";

export default function ExportDataPublisher({ data }: { data: ExportData }) {
  const { setExportData } = useExportDataContext();

  useEffect(() => {
    setExportData(data);
    return () => setExportData(null);
  }, [data, setExportData]);

  return null;
}
