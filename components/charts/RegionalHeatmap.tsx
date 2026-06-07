"use client";

import ReactECharts from "echarts-for-react";
import { useMemo } from "react";

/**
 * RegionalHeatmap — Mapa de calor do Brasil por intensidade cultural.
 * Usa ECharts Map com dados geográficos do Brasil (GeoJSON).
 *
 * Os dados são um array de { estado: "SP", valor: 0.87 }.
 * O GeoJSON do Brasil é registrado uma vez via echarts.registerMap().
 */
export interface RegionalData {
  estado: string; // sigla ex: "SP", "RJ", "AM"
  valor:  number; // 0–1
  label?: string; // texto opcional ex: "funk carioca"
}

interface Props {
  data: RegionalData[];
  title?: string;
  height?: number;
}

// Mapeamento sigla → nome completo (usado pelo GeoJSON do IBGE)
const ESTADO_NOMES: Record<string, string> = {
  AC:"Acre",AL:"Alagoas",AP:"Amapá",AM:"Amazonas",BA:"Bahia",
  CE:"Ceará",DF:"Distrito Federal",ES:"Espírito Santo",GO:"Goiás",
  MA:"Maranhão",MT:"Mato Grosso",MS:"Mato Grosso do Sul",MG:"Minas Gerais",
  PA:"Pará",PB:"Paraíba",PR:"Paraná",PE:"Pernambuco",PI:"Piauí",
  RJ:"Rio de Janeiro",RN:"Rio Grande do Norte",RS:"Rio Grande do Sul",
  RO:"Rondônia",RR:"Roraima",SC:"Santa Catarina",SP:"São Paulo",
  SE:"Sergipe",TO:"Tocantins",
};

export default function RegionalHeatmap({
  data,
  title = "Intensidade Cultural por Estado",
  height = 420,
}: Props) {
  const option = useMemo(() => {
    const mapData = data.map((d) => ({
      name:  ESTADO_NOMES[d.estado] ?? d.estado,
      value: Math.round(d.valor * 100),
      label_text: d.label ?? "",
    }));

    return {
      title: {
        text: title,
        left: "center",
        top: 8,
        textStyle: { fontSize: 13, color: "#374151", fontWeight: "600" },
      },
      tooltip: {
        trigger: "item",
        formatter: (p: { name: string; value: number; data?: { label_text: string } }) =>
          `<b>${p.name}</b><br/>Score: ${p.value ?? "—"}/100${
            p.data?.label_text ? `<br/>${p.data.label_text}` : ""
          }`,
      },
      visualMap: {
        min: 0,
        max: 100,
        left: "left",
        bottom: 20,
        text: ["Alto", "Baixo"],
        textStyle: { color: "#6B7280", fontSize: 11 },
        inRange: {
          color: ["#EDE9FE", "#7C3AED"],
        },
        calculable: true,
      },
      series: [
        {
          type: "map",
          map: "Brazil",
          name: "Score Cultural",
          data: mapData,
          emphasis: {
            label: { show: true, fontSize: 10 },
            itemStyle: { areaColor: "#F59E0B" },
          },
          select: { disabled: true },
          label: { show: false },
          itemStyle: {
            areaColor: "#F3F4F6",
            borderColor: "#D1D5DB",
            borderWidth: 0.5,
          },
        },
      ],
    };
  }, [data, title]);

  return (
    <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
      {/* Aviso: GeoJSON do Brasil deve ser carregado via useEffect antes de renderizar */}
      <BrazilMapLoader>
        <ReactECharts option={option} style={{ height }} notMerge />
      </BrazilMapLoader>
    </div>
  );
}

/**
 * Carrega o GeoJSON do Brasil assincronamente e registra no ECharts.
 * Fonte: IBGE simplificado (hospedado junto ao projeto ou CDN).
 */
function BrazilMapLoader({ children }: { children: React.ReactNode }) {
  // Importação dinâmica do GeoJSON — executada uma vez no client
  if (typeof window !== "undefined") {
    import("echarts").then((ec) => {
      if (!(ec as any).__brazil_registered) {
        fetch("/geo/brazil.json")
          .then((r) => r.json())
          .then((geo) => {
            ec.registerMap("Brazil", geo);
            (ec as any).__brazil_registered = true;
          })
          .catch(() => {
            // Fallback: usa mapa vazio (não quebra o app)
            ec.registerMap("Brazil", { type: "FeatureCollection", features: [] } as any);
          });
      }
    });
  }
  return <>{children}</>;
}
