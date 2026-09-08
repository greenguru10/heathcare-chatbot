import React, { useState, useEffect } from 'react';
import { SourceItem, CategoryItem } from '../types';
import { fetchSources, fetchCategories } from '../api/client';
import { Database, ShieldCheck, ExternalLink, Filter, Search, Award } from 'lucide-react';

export const SourceExplorerPage: React.FC = () => {
  const [sources, setSources] = useState<SourceItem[]>([]);
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTier, setSelectedTier] = useState<string>('all');

  useEffect(() => {
    async function loadData() {
      try {
        const [srcs, cats] = await Promise.all([fetchSources(), fetchCategories()]);
        setSources(srcs);
        setCategories(cats);
      } catch (err) {
        console.error('Failed to load sources or categories', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const filteredSources = sources.filter((s) => {
    const matchesSearch =
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.base_url.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTier = selectedTier === 'all' || s.authority_tier === selectedTier;
    return matchesSearch && matchesTier;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-in fade-in duration-200">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2.5 text-teal-800">
            <div className="p-2 bg-teal-100 text-teal-800 rounded-xl shadow-2xs">
              <Database className="w-5 h-5" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight font-display">
              Authoritative Source Library
            </h1>
          </div>
          <p className="text-xs text-slate-600 mt-1">
            Curated, tier-governed public health organizations and peer-reviewed publishers permitted in the RAG corpus.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search publisher or domain..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-3 py-2 text-xs bg-white border border-slate-300 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-teal-600 transition-colors shadow-2xs"
            />
          </div>

          <select
            value={selectedTier}
            onChange={(e) => setSelectedTier(e.target.value)}
            className="text-xs bg-white border border-slate-300 rounded-xl px-3 py-2 text-slate-800 focus:outline-none focus:border-teal-600 transition-colors shadow-2xs"
          >
            <option value="all">All Authority Tiers</option>
            <option value="A">Tier A (Global & National Agencies)</option>
            <option value="B">Tier B (Clinical Societies & Peer-Reviewed)</option>
            <option value="C">Tier C (Academic Medical Centers)</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-20 text-slate-400 text-xs flex items-center justify-center gap-2">
          <div className="w-4 h-4 border-2 border-teal-600 border-t-transparent rounded-full animate-spin" />
          <span>Loading verified registry...</span>
        </div>
      ) : (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSources.map((src) => (
            <div
              key={src.id}
              className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs hover:shadow-sm hover:border-teal-300 transition-all duration-150 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2.5">
                  <span className="flex items-center gap-1 text-[11px] font-bold text-teal-800 bg-teal-50 px-2.5 py-0.5 rounded-full border border-teal-200">
                    <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
                    Tier {src.authority_tier}
                  </span>
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider bg-slate-100 px-2 py-0.5 rounded-md">
                    {src.source_type}
                  </span>
                </div>

                <h3 className="font-bold text-slate-900 text-base mb-1 font-display">{src.name}</h3>
                <a
                  href={src.base_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-teal-700 hover:text-teal-900 font-medium hover:underline flex items-center gap-1 mb-3"
                >
                  <span className="truncate">{src.base_url}</span>
                  <ExternalLink className="w-3 h-3 flex-shrink-0" />
                </a>

                {src.license_notes && (
                  <p className="text-[11.5px] text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-100 mb-3 leading-relaxed">
                    <strong className="text-slate-800">Policy:</strong> {src.license_notes}
                  </p>
                )}
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="text-slate-500 font-medium">Authority Weight:</span>
                <span className="font-bold text-teal-800 flex items-center gap-1">
                  <Award className="w-3.5 h-3.5 text-teal-600" />
                  {Math.round(src.authority_score * 100)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Categories Summary */}
      <div className="mt-12 pt-6 border-t border-slate-200">
        <h2 className="text-base font-bold text-slate-900 mb-3 font-display">
          Approved Health Category Taxonomies ({categories.length})
        </h2>
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <div
              key={cat.id}
              className="bg-white border border-slate-200 px-3 py-1.5 rounded-xl text-xs text-slate-700 font-medium shadow-2xs hover:border-teal-300 transition-colors"
            >
              <strong className="text-slate-900">{cat.display_name}</strong>
              <span className="text-slate-400 ml-1.5 text-[11px]">({cat.slug})</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
