import React from 'react';
import { SourceCitation } from '../types';
import { X, ExternalLink, ShieldCheck, Calendar, BookOpen, Layers, Copy, Check } from 'lucide-react';

interface SourceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  sources: SourceCitation[];
  highlightedKey?: string;
}

export const SourceDrawer: React.FC<SourceDrawerProps> = ({
  isOpen,
  onClose,
  sources,
  highlightedKey
}) => {
  const [copiedKey, setCopiedKey] = React.useState<string | null>(null);

  if (!isOpen) return null;

  const copyExcerpt = (key: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white border-l border-slate-200 shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
      {/* Drawer Header */}
      <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-teal-100 text-teal-800 rounded-xl shadow-2xs">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900 font-display">Verified Evidence Literature</h2>
            <p className="text-xs text-slate-500">
              {sources.length} authoritative peer-reviewed source(s)
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-200 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Drawer Body Scroll */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {sources.length === 0 ? (
          <div className="text-center py-16 text-slate-400 text-xs">
            <Layers className="w-8 h-8 mx-auto mb-2 opacity-40" />
            No citations attached to this response.
          </div>
        ) : (
          sources.map((src) => {
            const isHighlighted = highlightedKey === src.citation_key;
            return (
              <div
                key={src.citation_key}
                id={`source-${src.citation_key}`}
                className={`p-4 rounded-2xl border transition-all duration-150 ${
                  isHighlighted
                    ? 'bg-teal-50/80 border-teal-400 shadow-md ring-2 ring-teal-400/20'
                    : 'bg-white border-slate-200 hover:border-slate-300 shadow-xs'
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="px-2 py-0.5 text-xs font-bold bg-teal-100 text-teal-800 rounded-md border border-teal-200">
                    [{src.citation_key}]
                  </span>
                  <span className="flex items-center gap-1 text-[11px] font-semibold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-full border border-teal-200">
                    <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
                    Tier {src.authority_tier} Authority
                  </span>
                </div>

                <h3 className="text-sm font-bold text-slate-900 leading-snug mb-1">
                  {src.title}
                </h3>
                <p className="text-xs font-medium text-slate-600 mb-2">
                  {src.source_name} {src.section ? `• Section: ${src.section}` : ''}
                </p>

                {src.excerpt && (
                  <div className="bg-slate-50 border border-slate-200/90 rounded-xl p-3 my-2.5 text-xs text-slate-700 leading-relaxed italic relative group">
                    "{src.excerpt}"
                    <button
                      onClick={() => copyExcerpt(src.citation_key, src.excerpt)}
                      className="absolute top-2 right-2 p-1 bg-white hover:bg-slate-100 text-slate-500 rounded border border-slate-200 opacity-0 group-hover:opacity-100 transition-opacity"
                      title="Copy excerpt"
                    >
                      {copiedKey === src.citation_key ? (
                        <Check className="w-3 h-3 text-teal-600" />
                      ) : (
                        <Copy className="w-3 h-3" />
                      )}
                    </button>
                  </div>
                )}

                <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-100">
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    <span>{src.last_updated || src.publication_date || 'Current'}</span>
                  </div>
                  {src.url && (
                    <a
                      href={src.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-teal-700 hover:text-teal-900 font-semibold hover:underline"
                    >
                      <span>Official Registry</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
