"use client";

import React, { useState } from 'react';
import { CheckCircle2, Calendar, Link as LinkIcon, DollarSign, Target, X } from 'lucide-react';

interface StrategicActionFormProps {
  onClose: () => void;
  onSubmit: (data: any) => void;
  hypothesisX: string;
}

export default function StrategicActionForm({ onClose, onSubmit, hypothesisX }: StrategicActionFormProps) {
  const [formData, setFormData] = useState({
    actionName: "",
    actionType: "Campaign",
    investment: "",
    channel: "Social Media",
    targetAudience: "",
    referenceLink: "",
    implementationDate: new Date().toISOString().split('T')[0],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-[32px] w-full max-w-lg overflow-hidden shadow-2xl animate-in zoom-in-95 duration-200">
        <div className="bg-violet-600 px-8 py-6 text-white flex justify-between items-center">
          <div>
            <h3 className="text-xl font-black">Registrar Ação Estratégica</h3>
            <p className="text-violet-100 text-xs font-medium">Conectando sua execução ao Alpha Slope</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-8 space-y-5">
          <div className="bg-violet-50 p-4 rounded-2xl border border-violet-100 mb-2">
            <p className="text-[10px] font-black text-violet-400 uppercase tracking-widest mb-1">Contexto da Hipótese</p>
            <p className="text-xs text-violet-700 font-medium italic">
              "Validando impacto da ação sobre: {hypothesisX}"
            </p>
          </div>

          <div className="space-y-4">
            <div className="space-y-1">
              <label className="text-[10px] font-black text-gray-400 uppercase">Nome da Ação / Campanha</label>
              <input
                required
                className="w-full p-3 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-violet-500 outline-none transition-all text-sm"
                placeholder="Ex: Manifesto Novo Luxo"
                value={formData.actionName}
                onChange={e => setFormData({...formData, actionName: e.target.value})}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-[10px] font-black text-gray-400 uppercase flex items-center gap-1">
                  <DollarSign size={10} /> Investimento (R$)
                </label>
                <input
                  type="number"
                  className="w-full p-3 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-violet-500 outline-none text-sm"
                  placeholder="0.00"
                  value={formData.investment}
                  onChange={e => setFormData({...formData, investment: e.target.value})}
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-black text-gray-400 uppercase flex items-center gap-1">
                  <Calendar size={10} /> Data Início
                </label>
                <input
                  type="date"
                  className="w-full p-3 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-violet-500 outline-none text-sm"
                  value={formData.implementationDate}
                  onChange={e => setFormData({...formData, implementationDate: e.target.value})}
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-black text-gray-400 uppercase flex items-center gap-1">
                <Target size={10} /> Canal Principal
              </label>
              <select
                className="w-full p-3 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-violet-500 outline-none text-sm"
                value={formData.channel}
                onChange={e => setFormData({...formData, channel: e.target.value})}
              >
                <option>Social Media</option>
                <option>OOH / Rua</option>
                <option>PR / Influência</option>
                <option>Conteúdo Próprio</option>
                <option>Comunidades</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-black text-gray-400 uppercase flex items-center gap-1">
                <LinkIcon size={10} /> Link de Referência (Opcional)
              </label>
              <input
                className="w-full p-3 bg-gray-50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-violet-500 outline-none text-sm"
                placeholder="https://suacampanha.com"
                value={formData.referenceLink}
                onChange={e => setFormData({...formData, referenceLink: e.target.value})}
              />
            </div>
          </div>

          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-4 bg-gray-100 hover:bg-gray-200 text-gray-600 font-bold rounded-2xl transition-all"
            >
              CANCELAR
            </button>
            <button
              type="submit"
              className="flex-[2] py-4 bg-violet-600 hover:bg-violet-700 text-white font-black rounded-2xl shadow-lg shadow-violet-200 transition-all flex items-center justify-center gap-2"
            >
              <CheckCircle2 size={18} /> CONFIRMAR REGISTRO
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
