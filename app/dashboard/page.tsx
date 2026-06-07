"use client";

import React, { useState, useEffect } from 'react';
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import MarketGapChart from "@/components/charts/MarketGapChart";
import SignalNetworkGraph from "@/components/charts/SignalNetworkGraph";
import IntelligenceStatusBar from "@/components/dashboard/IntelligenceStatusBar";
import GlobalSignalFilter from "@/components/dashboard/GlobalSignalFilter";
import BrazilianCulturalTwin from "@/components/intelligence/BrazilianCulturalTwin";
import ConversationalPrompt from "@/components/intelligence/ConversationalPrompt";
import { Search, Target, Rocket, RefreshCw, MessageSquare, TrendingUp, ChevronRight, Zap, Activity } from 'lucide-react';
import SignalNatureClassification from "@/components/charts/SignalNatureClassification";
import SignalChannelDistribution from "@/components/charts/SignalChannelDistribution";
import MaterializationCard from "@/components/dashboard/MaterializationCard";
import StrategicActionForm from "@/components/dashboard/StrategicActionForm";
import useDashboardSupabaseClient from "@/components/dashboard/useDashboardSupabaseClient";
import { runPreventiveAnalysis, PulseAnalysisResult } from "@/lib/pulse-api";

const PILLARS = [
	{
		id: "signals",
		href: "/dashboard/signals",
		title: "Sinais & Estabilidade",
		question: "Como estÃ¡ o pulso cultural hoje e quais sÃ£o os riscos?",
		subQuestions: [
			"Quais sinais fracos estÃ£o ganhando momento?",
			"Existe risco de instabilidade cultural iminente?",
			"Como os cÃ­rculos estÃ£o se comportando em tempo real?",
		],
		description:
			"Monitore a base de sinais culturais verificados e a saÃºde do ecossistema.",
		bgGradient: "from-blue-50 to-blue-100/50",
		borderColor: "border-blue-200",
		hoverBorder: "hover:border-blue-400",
		iconBg: "bg-blue-100",
		textColor: "text-blue-700",
		subtextColor: "text-blue-500",
		iconLetter: "S",
	},
	{
		id: "trends",
		href: "/dashboard/trends",
		title: "TendÃªncias",
		question: "Quais sÃ£o as grandes narrativas emergentes para o futuro?",
		subQuestions: [
			"Quais agrupamentos de sinais formam novas tendÃªncias?",
			"Qual Ã© a velocidade de adoÃ§Ã£o destas narrativas?",
			"Onde estÃ£o as oportunidades de inovaÃ§Ã£o?",
		],
		description: "Investigue tendÃªncias profundas e o Radar de EmergÃªncia (V9.9).",
		bgGradient: "from-violet-50 to-violet-100/50",
		borderColor: "border-violet-200",
		hoverBorder: "hover:border-violet-400",
		iconBg: "bg-violet-100",
		textColor: "text-violet-700",
		subtextColor: "text-violet-500",
		iconLetter: "T",
	},
	{
		id: "alma",
		href: "/dashboard/alma",
		title: "Alma Brasileira",
		question: "Como o brasileiro realmente se sente e se expressa?",
		subQuestions: [
			"Qual Ã© a identidade cultural predominante neste contexto?",
			"Existem tensÃµes entre discurso e sentimento real?",
			"Como as personas sintÃ©ticas reagem a este cenÃ¡rio?",
		],
		description:
			"Deep-dive na psicologia e antropologia cultural do Brasil (Brazilian Twin).",
		bgGradient: "from-amber-50 to-amber-100/50",
		borderColor: "border-amber-200",
		hoverBorder: "hover:border-amber-400",
		iconBg: "bg-amber-100",
		textColor: "text-amber-700",
		subtextColor: "text-amber-500",
		iconLetter: "A",
	},
	{
		id: "clustering",
		href: "/dashboard/clustering",
		title: "Clustering & Grafos",
		question: "Como os pontos se conectam no mapa da cultura?",
		subQuestions: [
			"Quais cÃ­rculos estÃ£o colidindo ou se fundindo?",
			"Como a informaÃ§Ã£o viaja entre plataformas?",
			"Quais sÃ£o os nÃ³s centrais de influÃªncia?",
		],
		description: "Visualize as correlaÃ§Ãµes geomÃ©tricas e o Grafo Cultural (V9.5).",
		bgGradient: "from-emerald-50 to-emerald-100/50",
		borderColor: "border-emerald-200",
		hoverBorder: "hover:border-emerald-400",
		iconBg: "bg-emerald-100",
		textColor: "text-emerald-700",
		subtextColor: "text-emerald-500",
		iconLetter: "C",
	},
];

export default function DashboardPage() {
	const [selectedSignalId, setSelectedSignalId] = useState<string | null>(null);
	const [predictionMode, setPredictionMode] = useState<'none' | 'competitor' | 'economic'>('none');
	const [selectedState, setSelectedState] = useState<'SP' | 'RJ' | 'BA' | 'MG'>('SP');
	const [isActionFormOpen, setIsActionFormOpen] = useState(false);
	const [lastAction, setLastAction] = useState<any>(null);
	const { supabase, user: dashboardUser } = useDashboardSupabaseClient();
	const [user, setUser] = useState<any>(dashboardUser);
	const [latestProject, setLatestProject] = useState<any>(null);
	const [stats, setStats] = useState({ totalCount: 842, alphaForecast: 0.82, objectiveNarrative: "Exploração" });
	const [realAnalysis, setRealAnalysis] = useState<PulseAnalysisResult | null>(null);
	const [isLoadingApi, setIsLoadingApi] = useState(false);
	const [rofData, setRofData] = useState<any>(null); // [V10.2] ROF: Return on Future
	const [aakerMetrics, setAakerMetrics] = useState<any>(null); // [V10.3] Aaker Brand Equity
	const searchParams = useSearchParams();

	useEffect(() => {
		async function loadData() {
			try {
				// 1. Carregamento CrÃ­tico Inicial (UI RÃ¡pida)
				const { data: { user: userData } } = await supabase.auth.getUser();
				setUser(userData);

				const projectId = searchParams.get("projectId");
				if (projectId) {
					loadProjectFromQuery(projectId);
				}

				// 2. Carregamento em Background (Pesado)
				// NÃ£o bloqueia a renderizaÃ§Ã£o inicial do dashboard
				(async () => {
					try {
						setIsLoadingApi(true);

						const [analysis, countRes] = await Promise.all([
							runPreventiveAnalysis({
								brand_name: "Brasilidade Tech",
								campaign_name: "LanÃ§amento V10",
								content: "EstratÃ©gia de Corre Regional e ColisÃ£o Tribal",
								target_regions: [selectedState]
							}),
							supabase.from("cultural_signals").select("id", { count: "exact", head: true })
						]);
						if (analysis) setRealAnalysis(analysis);
					} catch (e) {
						console.error("Falha no background fetch");
					} finally {
						setIsLoadingApi(false);
					}
				})();
			} catch (err) {
				console.error("Falha ao carregar dados do dashboard", err);
				setUser(null);
				setLatestProject(null);
			}
		}
		loadData();
	}, [selectedState, searchParams]); // Recarrega quando o estado muda (Business Synthesis ativo)

	async function loadProjectFromQuery(projectId: string) {
		try {
			const res = await fetch(`/api/projects/${projectId}`);
			if (!res.ok) return;
			const payload = await res.json();
			const project = payload.data || payload;
			if (!project) return;
			setLatestProject({
				...project,
				strategic_kpis: project.analysis_data?.onboarding?.strategic_kpis || project.strategic_kpis || {}
			});
		} catch (error) {
			console.error("Erro ao carregar projeto via projectId:", error);
		}
	}

	const isFirstTime = !user;
	const userName = user?.user_metadata?.full_name || "Explorador";
	const strategicKpis = latestProject?.strategic_kpis || {};
  const activeLens = strategicKpis.dashboard_lens || "Exploração";
  const projectName = latestProject?.brand_name || "Brasilidade Tech";
  const sectorName = latestProject?.segment || latestProject?.sector || "Setor não identificado";
  const projectQuery = latestProject?.id ? `?projectId=${latestProject.id}` : "";
  const regionalNuances = {
    "MG": { color: "#10b981", label: "Corre Artesanal / Tradição", momentum: 0.70, collision: "Agritech + Gastronomia" }
  };

  const activeRegion = (regionalNuances as any)[selectedState];


  const personaFeedback = (realAnalysis?.regional_analysis as any)?.[selectedState]?.persona || (({
    "SP": { name: "Dona Maria", score: 82, text: "Gostei da 'VitÃ³ria Suada'. Mas 'Ganbiarra' parece coisa errada, prefiro 'Jeitinho de Vencer'." },
    "RJ": { name: "Clara", score: 92, text: "O Realismo Visceral me cansa, mas a 'VitÃ³ria Coletiva' Ã© o que me faz comprar." },
    "BA": { name: "Enzo", score: 71, text: "A 'Ganbiarra' Ã© o futuro! Ã‰ o hackerismo de quebrada que ninguÃ©m vÃª." },
    "MG": { name: "Seu JosÃ©", score: 78, text: "Sinto falta de falar da famÃ­lia no Corre, mas a entrega estÃ¡ no caminho certo." }
  } as any)[selectedState] || { name: "Explorador", score: 50, text: "Aguardando sinal regional..." });

  // ðŸ§  [V9.5] LÃ³gica de ConexÃ£o: SimulaÃ§Ã£o de Cadeia de Causalidade DinÃ¢mica
  const lensKey = (activeLens?.split(" ")[0] as "ExploraÃ§Ã£o" | "AÃ§Ã£o" | "ProteÃ§Ã£o") || "ExploraÃ§Ã£o";
  
  // Estrutura de HipÃ³tese V9.5: Conectando Fato Estranho (X) + Grupo (Y) + TensÃ£o (Z)
  const hypothesisData = (({
    "ExploraÃ§Ã£o": {
      x: "Cultura do 'Corre' Digital",
      y: "Jovens PerifÃ©ricos",
      z: "Necessidade de AscensÃ£o via Tech-Improviso"
    },
    "AÃ§Ã£o": {
      x: "Dumbphones / DesconexÃ£o",
      y: "Gen Z exausta",
      z: "Esgotamento DopaminÃ©rgico Digital"
    },
    "ProteÃ§Ã£o": {
      x: "Economia do Apego",
      y: "Consumidores Senior",
      z: "Incerteza InflacionÃ¡ria"
    }
  } as any)[lensKey] || { x: "", y: "", z: "" });

  const causalInsight = (({
    "ExploraÃ§Ã£o": {
      chain: "S -> P -> T (Cadeia de Ruptura)",
      why: "Sinal social desafia o status e abre novo nicho tech.",
      alpha: 0.85, slope: 0.12, noise: 0.05
    },
    "AÃ§Ã£o": {
      chain: "T -> S -> E (Cadeia de Oportunidade)",
      why: "InovaÃ§Ã£o tech acelera comportamento e gera ROI imediato.",
      alpha: 0.45, slope: 0.09, noise: 0.15
    },
    "ProteÃ§Ã£o": {
      chain: "E -> S -> P (Cadeia de ContenÃ§Ã£o)",
      why: "Choque econÃ´mico gera risco social e instabilidade.",
      alpha: 0.30, slope: 0.01, noise: 0.45
    }
  } as any)[lensKey] || { chain: "N/A", why: "Processando...", alpha: 0.5, slope: 0.05, noise: 0.1 });

  // ðŸ“ˆ [V9.5] LÃ³gica de Filtragem Baseada na HipÃ³tese (Active Learning)
  const filterSignalsByHypothesis = (rawSignals: any[]) => {
    return rawSignals.map(s => {
      const isCorroborating = s.insight.toLowerCase().includes(hypothesisData.z.toLowerCase().split(' ')[0]);
      return {
        ...s,
        relevanceScore: isCorroborating ? 1.0 : 0.4,
        strokeColor: isCorroborating ? '#8b5cf6' : 'transparent',
        strokeWidth: isCorroborating ? 3 : 0
      };
    });
  };

  const dashboardSignals = [
    { id: '1', label: 'E-Sports Regional', size: 45, color: '#10b981', x: 300, y: 120, category: 'Sociocultural', volume: 2847, tension: 'MÃ©dia', momentum: 78, insight: 'Novos clusters de consumo em cidades secundÃ¡rias.', harmonicFreq: 84.5, affinity: 92 },
    { id: '2', label: 'Pagode 90s Revival', size: 35, color: '#f59e0b', x: 480, y: 225, category: 'EconÃ´mico', volume: 1920, tension: 'Alta', momentum: 85, insight: 'Impacto direto em moda e nostalgia.', harmonicFreq: 72.1, affinity: 88 },
    { id: '3', label: 'IA para Pequenos', size: 28, color: '#3b82f6', x: 120, y: 225, category: 'Emocional', volume: 1540, tension: 'Baixa', momentum: 92, insight: 'Ansiedade vs Curiosidade produtiva.', harmonicFreq: 95.8, affinity: 97 },
    { id: '4', label: 'Bio-Arquitetura', size: 30, color: '#ef4444', x: 300, y: 350, category: 'Ambiental', volume: 1200, tension: 'MÃ©dia', momentum: 65, insight: 'ReconexÃ£o com origens no caos urbano.', harmonicFreq: 64.2, affinity: 75 },
    { id: '5', label: 'NFTs Educacionais', size: 40, color: '#3b82f6', x: 180, y: 280, category: 'Emocional', volume: 2100, tension: 'Alta', momentum: 78, insight: 'Utilidade alÃ©m da especulaÃ§Ã£o.', harmonicFreq: 88.4, affinity: 91 },
  ];

  const filteredSignals = filterSignalsByHypothesis(dashboardSignals);

	const sortedPillars = [...PILLARS].filter(p => !['alma', 'trends'].includes(p.id)).sort((a, b) => {
		if (activeLens.includes("AÃ§Ã£o") && a.id === "signals") return -1;
		if (activeLens.includes("ExploraÃ§Ã£o") && a.id === "clustering") return -1;
		if (activeLens.includes("ProteÃ§Ã£o") && a.id === "trends") return -1;
		return 0;
	});

	// ðŸ§© BLOCO DE HIPÃ“TESE (DIDÃTICO) + SISTEMA DE VALIDAÃ‡ÃƒO (V9.5)
	const validationStatus = {
		progress: causalInsight.slope > 0.1 ? 85 : 45,
		verdict: causalInsight.slope > 0.1 ? "HipÃ³tese Validada" : "HipÃ³tese em Teste",
		color: causalInsight.slope > 0.1 ? "text-emerald-600" : "text-amber-600",
		bg: causalInsight.slope > 0.1 ? "bg-emerald-50" : "bg-amber-50"
	};

	const handleActionSubmit = (data: any) => {
		console.log("AÃ§Ã£o registrada:", data);
		setLastAction(data);
		setIsActionFormOpen(false);

		// ðŸ“ˆ [V9.5] SimulaÃ§Ã£o de Ganho apÃ³s Registro de AÃ§Ã£o
		setStats(prev => ({
			...prev,
			alphaForecast: prev.alphaForecast * 1.25 // Simula o ganho de 25% visto no script
		}));
	};

	return (
		<main className="min-h-screen bg-[#FDFDFD] text-[#1A1A1A]">
			{isActionFormOpen && (
				<StrategicActionForm 
					onClose={() => setIsActionFormOpen(false)} 
					onSubmit={handleActionSubmit} 
					hypothesisX={hypothesisData.x}
				/>
			)}
			<div className="max-w-7xl mx-auto px-4 py-8 md:px-8">
				{/* 1. Header EstratÃ©gico & User Context */}
				<header className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-gray-100 pb-8">
					<div className="space-y-2">
						<div className="flex items-center gap-3">
							<div className="bg-violet-600/10 text-violet-600 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border border-violet-100">
								Status: {activeLens}
							</div>
						</div>
						<h1 className="text-4xl font-black tracking-tight text-gray-900">
							OlÃ¡, {userName.split(" ")[0]} 
							<span className="text-violet-600 ml-1">.</span>
						</h1>
						<p className="text-gray-400 font-medium text-lg">
							{isFirstTime 
								? "Sua inteligÃªncia cultural estÃ¡ pronta. Comece pelo 'Mapa de Sinais'." 
								: `Monitorando ${projectName} em ${sectorName}.`}
						</p>
					</div>

					{/* ðŸŽ¯ Status da Lente (Compacto & Contextual) - REPOSICIONADO V10.4 */}
					<div className="bg-violet-900 rounded-3xl p-5 text-white shadow-lg border border-white/10 flex items-center gap-6 min-w-[320px] relative overflow-hidden group hover:scale-[1.02] transition-transform">
						<div className="absolute right-0 top-0 opacity-10 translate-x-1/4 -translate-y-1/4 group-hover:scale-110 transition-transform duration-700">
							<Rocket size={120} />
						</div>
						<div className="flex-1 relative z-10">
							<div className="flex items-center gap-2 mb-1">
								<span className="text-[9px] font-black uppercase tracking-widest text-violet-300">Lente Ativa</span>
								<span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
							</div>
							<h3 className="text-xl font-black">{activeLens}</h3>
							<Link 
								href="/dashboard/methodology" 
								className="text-[10px] font-bold text-violet-300 hover:text-white flex items-center gap-1 mt-1 transition-colors group/link"
							>
								VER DEEP-DIVE <ChevronRight size={10} className="group-hover/link:translate-x-0.5 transition-transform" />
							</Link>
						</div>
					</div>
				</header>

				{/* 2. Intelligence Status Bar (Executive Dashboard Core) */}
				<IntelligenceStatusBar 
					totalSignals={stats.totalCount} 
					activeImpact={Math.round(stats.alphaForecast * 100)} 
					discoveryRate={selectedState} 
				/>

				{/* 2.2 REGIONAL SLICER & ROF (V10.2) */}
				<div className="mb-10 grid grid-cols-1 md:grid-cols-4 gap-4">
					<div className="md:col-span-3 bg-white rounded-3xl border border-gray-100 p-6 flex items-center justify-between shadow-sm">
						<div className="flex items-center gap-6">
							<div>
								<h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Regionalidade (Estado)</h4>
								<div className="flex gap-2">
									{(['SP', 'RJ', 'BA', 'MG'] as const).map(state => (
										<button 
											key={state}
											onClick={() => setSelectedState(state)}
											className={`w-12 h-12 rounded-xl text-xs font-black transition-all border ${selectedState === state ? 'bg-violet-600 text-white border-violet-700 shadow-md' : 'bg-gray-50 text-gray-400 border-gray-100 hover:bg-gray-100'}`}
										>
											{state}
										</button>
									))}
								</div>
							</div>
							<div className="h-10 w-px bg-gray-100" />
							<div>
								<h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest">AderÃªncia: {activeRegion.label}</h4>
								<div className="flex items-center gap-3">
									<div className="flex items-center gap-2">
										<span className="text-2xl font-black text-gray-900">{(activeRegion.momentum * 100).toFixed(0)}%</span>
										<TrendingUp size={14} className="text-emerald-500" />
									</div>
									<div className="bg-amber-100 text-amber-700 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-tighter border border-amber-200">
										ColisÃ£o: {activeRegion.collision}
									</div>
								</div>
							</div>
						</div>
						
						{/* [V10.2] ROF Badge */}
						<div className="h-full px-6 flex flex-col justify-center border-l border-gray-100">
							<h4 className="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1">ROF (Return on Future)</h4>
							<div className="flex items-baseline gap-1">
								<span className={`text-2xl font-black ${rofData?.color || 'text-gray-900'}`}>{rofData?.score}</span>
								<span className="text-[10px] font-bold text-gray-400">pts</span>
							</div>
							<p className="text-[8px] font-bold text-gray-500">Elasticidade: {rofData?.elasticity}</p>
						</div>
					</div>

					<div className="bg-violet-50 rounded-3xl border border-violet-100 p-6 shadow-sm relative overflow-hidden group/persona">
						<div className="flex items-center justify-between mb-2">
							<h4 className="text-[10px] font-black text-violet-400 uppercase tracking-widest">Crivo das Almas</h4>
							<span className={`text-[10px] font-black px-2 py-0.5 rounded-full bg-white text-violet-600 border border-violet-100`}>
								{personaFeedback.score}% AderÃªncia
							</span>
						</div>
						<p className="text-[11px] font-bold text-violet-900 leading-tight italic">
							"{personaFeedback.text}"
						</p>
						<p className="text-[9px] font-black text-violet-400 mt-2 uppercase">Persona: {personaFeedback.name}</p>
						<div className="absolute -right-2 -bottom-2 opacity-10 group-hover/persona:rotate-12 transition-transform">
							<MessageSquare size={48} className="text-violet-600" />
						</div>
					</div>
				</div>

				{/* 3. Alpha Prediction & Momentum Section */}
				<div className="bg-white rounded-3xl border border-gray-100 shadow-sm p-8 group hover:border-violet-100 transition-colors">
					<div className="flex items-center justify-between mb-8">
						<div>
							<h3 className="text-xl font-black text-gray-900 tracking-tight">ProjeÃ§Ã£o Cultural e Alpha Slope</h3>
							<p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-1">SimulaÃ§Ã£o Contrafactual de CenÃ¡rios (V9.6)</p>
						</div>
						<div className="flex items-center gap-2 bg-gray-50 p-1.5 rounded-2xl border border-gray-100">
							<button 
								onClick={() => setPredictionMode('none')}
								className={`px-4 py-2 text-[9px] font-black uppercase rounded-xl transition-all ${predictionMode === 'none' ? 'bg-white shadow-sm text-gray-900 border border-gray-100' : 'text-gray-400 hover:text-gray-600'}`}
							>
								Hoje
							</button>
							<button 
								onClick={() => setPredictionMode('competitor')}
								className={`px-4 py-2 text-[9px] font-black uppercase rounded-xl transition-all ${predictionMode === 'competitor' ? 'bg-red-500 text-white shadow-lg' : 'text-gray-400 hover:text-red-500'}`}
							>
								Concorrente
							</button>
							<button 
								onClick={() => setPredictionMode('economic')}
								className={`px-4 py-2 text-[9px] font-black uppercase rounded-xl transition-all ${predictionMode === 'economic' ? 'bg-emerald-500 text-white shadow-lg' : 'text-gray-400 hover:text-emerald-500'}`}
							>
								EconÃ´mico
							</button>
						</div>
					</div>
					<div className="grid grid-cols-1 md:grid-cols-3 gap-8">
						<div className="md:col-span-2">
							<MarketGapChart 
								alphaValue={causalInsight.alpha} 
								slopeValue={causalInsight.slope} 
								stdDevValue={causalInsight.noise}
								sectorName={projectName} 
								lensType={activeLens} 
								predictionMode={predictionMode}
							/>
						</div>
						<div className="flex flex-col justify-center space-y-4 border-l border-gray-50 pl-8">
							{/* ðŸ”® INSIGHT PREDITIVO (ACTIVE LEARNING) */}
							{predictionMode !== 'none' && (
								<div className={`p-5 rounded-3xl border animate-in fade-in slide-in-from-top-4 duration-500 ${predictionMode === 'competitor' ? 'bg-red-50 border-red-100' : 'bg-emerald-50 border-emerald-100'}`}>
									<div className="flex items-baseline gap-2 mb-2">
										<Zap size={14} className={predictionMode === 'competitor' ? 'text-red-500' : 'text-emerald-500'} />
										<h4 className={`text-[11px] font-black uppercase tracking-widest ${predictionMode === 'competitor' ? 'text-red-700' : 'text-emerald-700'}`}>
											{predictionMode === 'competitor' ? 'Alerta de ComoditizaÃ§Ã£o' : 'Janela de AceleraÃ§Ã£o'}
										</h4>
									</div>
									<p className={`text-[11px] font-medium leading-relaxed ${predictionMode === 'competitor' ? 'text-red-600' : 'text-emerald-600'}`}>
										{predictionMode === 'competitor' 
											? "Principal concorrente imitabilidade alta. SugestÃ£o: Migrar para sub-sinal 'Hackerismo'." 
											: "InflaÃ§Ã£o no Cluster Y gera hiper-traÃ§Ã£o no 'Corre'. SugestÃ£o: Implementar Refis de Marca."}
									</p>
								</div>
							)}
							{/* ðŸ§© MONITOR DE HIPÃ“TESE (ACTIVE LEARNING) */}
							<div className={`p-5 rounded-3xl border ${validationStatus.bg}`}>
								<div className="flex items-center justify-between mb-3">
									<h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest">SincronizaÃ§Ã£o da HipÃ³tese</h4>
									<span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-full ${validationStatus.color} bg-white/50 border border-current/10`}>
										{validationStatus.verdict}
									</span>
								</div>
								
								<p className="text-[11px] text-gray-700 leading-relaxed mb-4">
									"O fenÃ´meno <strong className="text-violet-600 font-black">{hypothesisData.x}</strong> no grupo <strong className="text-violet-600 font-bold">{hypothesisData.y}</strong> Ã© uma resposta Ã  <strong className="text-violet-600 font-bold">{hypothesisData.z}</strong>."
								</p>

								{/* Barra de Progresso de ValidaÃ§Ã£o SemÃ¢ntica */}
								<div className="space-y-1.5">
									<div className="flex justify-between text-[9px] font-black uppercase text-gray-400">
										<span>ConfianÃ§a do CÃ©rebro IA</span>
										<span className={validationStatus.color}>{validationStatus.progress}%</span>
									</div>
									<div className="h-2 w-full bg-gray-200/50 rounded-full overflow-hidden p-0.5">
										<div 
											className={`h-full rounded-full transition-all duration-1000 ${causalInsight.slope > 0.1 ? 'bg-emerald-500' : 'bg-amber-500'}`}
											style={{ width: `${validationStatus.progress}%` }}
										/>
									</div>
								</div>
							</div>

							<div className="p-4 bg-violet-50 rounded-2xl border border-violet-100">
								<h4 className="text-[10px] font-black text-violet-400 uppercase tracking-widest mb-1">Cadeia de Causalidade</h4>
								<p className="text-xl font-black text-violet-700">{causalInsight.chain}</p>
								<p className="text-[10px] text-violet-500 mt-1 font-medium italic">"{causalInsight.why}"</p>
							</div>

							{/* ðŸ”„ LOOP DE IMPLEMENTAÃ‡ÃƒO (O QUE FOI FEITO) */}
							<div className="p-4 bg-white rounded-2xl border border-gray-100 shadow-sm relative overflow-hidden group/exec">
								<div className="flex items-center gap-2 mb-2 relative z-10">
									<RefreshCw size={12} className={`text-violet-500 ${lastAction ? '' : 'animate-spin-slow'}`} />
									<h4 className="text-[10px] font-black text-gray-400 uppercase tracking-widest">ExecuÃ§Ã£o EstratÃ©gica</h4>
								</div>
								<div className="space-y-2 relative z-10">
									{lastAction ? (
										<div className="bg-emerald-50/50 p-3 rounded-xl border border-emerald-100 animate-in fade-in slide-in-from-right-2">
											<p className="text-[10px] font-bold text-emerald-700">AÃ§Ã£o: {lastAction.actionName}</p>
											<p className="text-[9px] text-emerald-500 font-medium italic mt-0.5">
												Registrada em {lastAction.implementationDate} no canal {lastAction.channel}.
											</p>
											<div className="mt-2 flex items-center gap-1.5">
												<div className="h-1 flex-1 bg-emerald-100 rounded-full overflow-hidden">
													<div className="h-full bg-emerald-500 animate-pulse w-[100%]" />
												</div>
												<span className="text-[8px] font-black text-emerald-600 uppercase">Aguardando Impacto...</span>
											</div>
										</div>
									) : (
										<p className="text-[10px] font-medium text-gray-500 italic">"ApÃ³s implementar a recomendaÃ§Ã£o, registre aqui para medir o impacto no Alpha Slope."</p>
									)}
									<button 
										onClick={() => setIsActionFormOpen(true)}
										className="w-full py-2 bg-gray-900 text-white text-[10px] font-black uppercase rounded-lg hover:bg-violet-600 transition-colors"
									>
										{lastAction ? "Atualizar AÃ§Ã£o Realizada" : "Registrar AÃ§Ã£o Realizada"}
									</button>
								</div>
							</div>
						</div>
					</div>
				</div>

				{/* 3.5 MATERIALIZATION V9 - AÃ§Ã£o EstratÃ©gica Baseada na Lente */}
				<div className="my-10">
					<MaterializationCard 
						projectId={latestProject?.id ?? ""}
						brandName={projectName}
						currentGoal={activeLens}
						onboardingContext={latestProject?.objective || "Mercado Consumidor Brasil"}
					/>
				</div>

				{/* 4. Signal Analysis - Network Graph (V10.5) */}
				<div className="my-10">
					<div className="flex items-center justify-between mb-6">
						<div>
							<h2 className="text-2xl font-black text-gray-900 tracking-tight">AnÃ¡lise de Sinais</h2>
							<p className="text-sm text-gray-400 font-medium italic">Geometria de adjacÃªncia e grafos culturais</p>
						</div>
					</div>
					<div className="space-y-8">
						{/* Evento onNodeClick atualiza o estado via Client Side */}
						<div className="min-h-[750px] w-full bg-white rounded-[40px] border border-gray-100 shadow-sm overflow-hidden">
							<SignalNetworkGraph 
								onNodeClick={(id) => setSelectedSignalId(id)} 
								signals={filteredSignals}
							/>
						</div>
						
						{/* SequÃªncia vertical solicitada: Natureza -> Canais -> Radar */}
						<div className="flex flex-col gap-12">
							{/* 2. Signal Nature (v9.8) */}
							<div className="min-h-[600px] w-full bg-white rounded-[40px] border border-gray-100 shadow-sm p-8 overflow-hidden transition-all hover:border-violet-100">
								<SignalNatureClassification selectedSignalId={selectedSignalId} />
							</div>

							{/* 3. Signal Distribution Channels (v10.1) */}
							<div className="min-h-[600px] w-full bg-white rounded-[40px] border border-gray-100 shadow-sm p-8 overflow-hidden transition-all hover:border-violet-100">
								<SignalChannelDistribution />
							</div>
						</div>
					</div>
				</div>

				<div className="border-t pt-10">
					<h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
						Acesso rapido
					</h3>
					<div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
						{[
							{ href: "/dashboard/signals" + projectQuery, label: "Sinais" },
							{ href: "/dashboard/circles" + projectQuery, label: "Cirulos" },
							{ href: "/dashboard/projects" + projectQuery, label: "Projetos" },
							{ href: "/dashboard/trends" + projectQuery, label: "Tendencias" },
							{ href: "/dashboard/stability-risk" + projectQuery, label: "Estab. x Risco" },
							{ href: "/dashboard/strategy-learning" + projectQuery, label: "Aprendizado" },
						].map((item) => (
							<Link
								key={item.href}
								href={item.href}
								className="bg-white rounded-xl border border-gray-100 px-3 py-2.5 text-xs font-medium text-gray-600 hover:border-gray-300 hover:text-gray-900 transition text-center"
							>
								{item.label}
							</Link>
						))}
					</div>
				</div>

				{/* ðŸ¤– Active Learning Interface */}
				<ConversationalPrompt />
			</div>
		</main>
	);
}

