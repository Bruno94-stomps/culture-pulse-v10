"use client";

import { Rocket, Search, ShieldCheck } from "lucide-react";

const SCENARIOS = [
  {
    id: "launch",
    title: "Lançamento de Produto",
    icon: Rocket,
    color: "bg-blue-500",
    description: "Foco em viralidade, aceitação de novos nichos e tendências de consumo.",
    example: "Ex: Novo energético para gamers em SP."
  },
  {
    id: "research",
    title: "Pesquisa de Mercado",
    icon: Search,
    color: "bg-purple-500",
    description: "Mapeamento profundo de hábitos, dores e círculos culturais dominantes.",
    example: "Ex: Comportamento de cosméticos em Salvador."
  },
  {
    id: "reputation",
    title: "Crise de Reputação",
    icon: ShieldCheck,
    color: "bg-red-500",
    description: "Monitoramento de tensões, sentimentos negativos e recuperação de imagem.",
    example: "Ex: Reação do público a mudanças na embalagem."
  }
];

interface ScenarioSelectorProps {
  selectedId: string;
  onSelect: (id: string) => void;
}

export default function ScenarioSelector({ selectedId, onSelect }: ScenarioSelectorProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {SCENARIOS.map((scenario) => {
        const Icon = scenario.icon;
        const active = selectedId === scenario.id;
        
        return (
          <button
            key={scenario.id}
            onClick={() => onSelect(scenario.id)}
            className={`flex flex-col p-4 rounded-2xl border-2 text-left transition-all ${
              active 
                ? "border-violet-500 bg-violet-50/50 ring-4 ring-violet-100" 
                : "border-gray-100 bg-white hover:border-violet-200"
            }`}
          >
            <div className={`p-2 rounded-lg w-fit mb-3 ${scenario.color} text-white`}>
              <Icon size={20} />
            </div>
            <h3 className="font-bold text-gray-900 mb-1">{scenario.title}</h3>
            <p className="text-xs text-gray-500 leading-relaxed mb-3">{scenario.description}</p>
            <div className={`mt-auto text-[10px] font-medium px-2 py-1 rounded-md ${
              active ? "bg-violet-100 text-violet-700" : "bg-gray-50 text-gray-400"
            }`}>
              {scenario.example}
            </div>
          </button>
        );
      })}
    </div>
  );
}
