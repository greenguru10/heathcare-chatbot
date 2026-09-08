import React from 'react';
import {
  ShieldCheck,
  Database,
  MessageSquare,
  Info,
  HeartPulse,
  Sparkles
} from 'lucide-react';

interface TopNavigationProps {
  currentTab: 'chat' | 'sources';
  setCurrentTab: (tab: 'chat' | 'sources') => void;
  onOpenPrivacy: () => void;
}

export const TopNavigation: React.FC<TopNavigationProps> = ({
  currentTab,
  setCurrentTab,
  onOpenPrivacy
}) => {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-13 flex items-center justify-between">
        {/* Brand Logo */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-teal-700 to-teal-500 flex items-center justify-center text-white shadow-xs">
            <HeartPulse className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-display font-bold text-slate-900 text-base tracking-tight">
                Health<span className="text-teal-700">Evidence</span>
              </span>
              <span className="text-[9.5px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200/80 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-teal-600" />
                Verified RAG
              </span>
            </div>
          </div>
        </div>

        {/* Center Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-slate-100/90 p-1 rounded-xl border border-slate-200 text-xs font-semibold">
          <button
            onClick={() => setCurrentTab('chat')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg transition-all ${
              currentTab === 'chat'
                ? 'bg-white text-teal-800 shadow-xs border border-slate-200/60'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Consultation</span>
          </button>
          <button
            onClick={() => setCurrentTab('sources')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg transition-all ${
              currentTab === 'sources'
                ? 'bg-white text-teal-800 shadow-xs border border-slate-200/60'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            <span>Source Library</span>
          </button>
        </nav>

        {/* Right Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={onOpenPrivacy}
            className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-teal-800 font-medium px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 transition-all shadow-2xs"
          >
            <Info className="w-3.5 h-3.5 text-slate-500" />
            <span className="hidden sm:inline">Safety & Privacy</span>
          </button>
        </div>
      </div>
    </header>
  );
};
