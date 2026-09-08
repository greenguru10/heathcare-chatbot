import React, { useState } from 'react';
import { ConfidenceInfo } from '../types';
import { CheckCircle2, AlertTriangle, HelpCircle, ShieldCheck } from 'lucide-react';

interface ConfidenceBadgeProps {
  confidence: ConfidenceInfo;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ confidence }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  const getStyle = () => {
    switch (confidence.label) {
      case 'high':
        return {
          bg: 'bg-teal-50 border-teal-200 text-teal-800',
          dot: 'bg-teal-500',
          icon: <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />,
          text: 'High Evidence Support'
        };
      case 'medium':
        return {
          bg: 'bg-amber-50 border-amber-200 text-amber-800',
          dot: 'bg-amber-500',
          icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />,
          text: 'Moderate Evidence Support'
        };
      case 'low':
        return {
          bg: 'bg-orange-50 border-orange-200 text-orange-800',
          dot: 'bg-orange-500',
          icon: <HelpCircle className="w-3.5 h-3.5 text-orange-600" />,
          text: 'Limited Evidence'
        };
      default:
        return {
          bg: 'bg-slate-100 border-slate-200 text-slate-700',
          dot: 'bg-slate-400',
          icon: <HelpCircle className="w-3.5 h-3.5 text-slate-500" />,
          text: 'Insufficient Evidence'
        };
    }
  };

  const style = getStyle();

  return (
    <div className="relative inline-block">
      <button
        type="button"
        onClick={() => setShowTooltip(!showTooltip)}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${style.bg} transition-all hover:shadow-sm cursor-pointer`}
      >
        {style.icon}
        <span>{style.text}</span>
        <span className="text-[10px] font-bold opacity-75">({Math.round(confidence.score * 100)}%)</span>
      </button>

      {showTooltip && (
        <div className="absolute left-0 bottom-full mb-2 z-50 w-72 p-3 bg-slate-900 text-slate-100 text-xs rounded-xl shadow-xl border border-slate-800 animate-in fade-in zoom-in-95 duration-150">
          <p className="font-semibold text-teal-300 mb-1">Grounded Confidence Evaluation</p>
          <p className="text-slate-300 leading-relaxed">{confidence.explanation}</p>
          <div className="mt-2 pt-2 border-t border-slate-800 text-[10px] text-slate-400">
            Calculated deterministically from source tier authority, lexical overlap, and claim support.
          </div>
        </div>
      )}
    </div>
  );
};
