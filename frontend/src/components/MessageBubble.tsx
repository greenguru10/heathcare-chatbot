import React, { useState } from 'react';
import { ChatMessage, SourceCitation } from '../types';
import { ConfidenceBadge } from './ConfidenceBadge';
import { CitationBadge } from './CitationBadge';
import { EmergencyAlert } from './EmergencyAlert';
import {
  ThumbsUp,
  ThumbsDown,
  Stethoscope,
  User,
  AlertCircle,
  Sparkles,
  Copy,
  Check,
  Volume2,
  VolumeX,
  ExternalLink,
  BookOpen
} from 'lucide-react';

interface MessageBubbleProps {
  message: ChatMessage;
  onCitationClick: (key: string, sources: SourceCitation[]) => void;
  onOpenFeedback: (answerId: string) => void;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  onCitationClick,
  onOpenFeedback
}) => {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  // Copy answer to clipboard
  const handleCopy = () => {
    if (!message.content) return;
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Text to speech playback
  const handleToggleSpeech = () => {
    if (!window.speechSynthesis) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    const cleanText = message.content.replace(/\[S\d+\]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
    setIsSpeaking(true);
  };

  // Helper to render text with clickable [S#] badges
  const renderTextWithCitations = (text: string) => {
    if (!text) return null;
    const parts = text.split(/(\[S\d+\])/g);
    return parts.map((part, index) => {
      const match = part.match(/^\[(S\d+)\]$/);
      if (match) {
        const key = match[1];
        const matchedSource = (message.sources || []).find((s) => s.citation_key === key);
        return (
          <CitationBadge
            key={index}
            citationKey={key}
            sourceTitle={matchedSource?.title}
            sourcePublisher={matchedSource?.source_name}
            onClick={() => onCitationClick(key, message.sources || [])}
          />
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  // Format key points text cleanly
  const formatKeyPointText = (text: string) => {
    // If point has internal newlines or dashes, split and format cleanly
    const lines = text.split('\n').filter((l) => l.trim().length > 0);
    if (lines.length > 1) {
      return (
        <div className="space-y-1">
          {lines.map((line, idx) => {
            const cleanLine = line.replace(/^[-•*]\s*/, '').trim();
            return (
              <div key={idx} className="leading-relaxed">
                {renderTextWithCitations(cleanLine)}
              </div>
            );
          })}
        </div>
      );
    }
    return renderTextWithCitations(text.replace(/^[-•*]\s*/, '').trim());
  };

  if (isUser) {
    return (
      <div className="flex items-start justify-end gap-3 my-4 animate-in fade-in slide-in-from-bottom-1 duration-150">
        <div className="max-w-xl bg-teal-700 text-white rounded-2xl rounded-tr-sm px-5 py-3 shadow-xs text-[14px] leading-relaxed font-normal break-words">
          {message.content}
        </div>
        <div className="w-8 h-8 rounded-xl bg-slate-800 text-white flex items-center justify-center flex-shrink-0 text-xs font-bold shadow-xs mt-0.5">
          <User className="w-4 h-4" />
        </div>
      </div>
    );
  }

  // Emergency / Red Flag Case
  if (message.response_mode === 'emergency' || message.risk_level === 'red') {
    return (
      <div className="flex items-start gap-3 my-4 animate-in fade-in slide-in-from-bottom-1 duration-150">
        <div className="w-8 h-8 rounded-xl bg-red-600 text-white flex items-center justify-center flex-shrink-0 shadow-sm mt-0.5">
          <AlertCircle className="w-4 h-4" />
        </div>
        <div className="flex-1 max-w-2xl sm:max-w-3xl">
          <EmergencyAlert answerText={message.content} />
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3.5 my-5 animate-in fade-in slide-in-from-bottom-1 duration-150">
      {/* Bot Avatar */}
      <div className="w-8 h-8 rounded-xl bg-teal-700 text-white flex items-center justify-center flex-shrink-0 shadow-xs mt-0.5">
        <Stethoscope className="w-4 h-4" />
      </div>

      <div className="flex-1 max-w-3xl space-y-3 min-w-0">
        {/* Reply Header / Brand & Confidence */}
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-900 tracking-tight">HealthEvidence</span>
            <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-teal-800 bg-teal-50 border border-teal-200/80 px-2 py-0.5 rounded-full">
              <Sparkles className="w-2.5 h-2.5 text-teal-600" />
              Verified RAG
            </span>
          </div>
          {message.confidence && <ConfidenceBadge confidence={message.confidence} />}
        </div>

        {/* Main Content Area */}
        <div className="space-y-3 text-slate-800">
          {/* Main Answer Paragraphs */}
          <div className="text-[14.5px] leading-relaxed text-slate-800 font-normal">
            {renderTextWithCitations(message.content)}
          </div>

          {/* Key Evidence Points (Clean list with left accent line) */}
          {message.key_points && message.key_points.length > 0 && (
            <div className="my-2.5 pl-3.5 border-l-2 border-teal-500 bg-teal-50/30 rounded-r-xl py-2 pr-3 space-y-1.5">
              <h4 className="text-[11px] font-bold text-teal-900 uppercase tracking-wider flex items-center gap-1.5 mb-1">
                <Sparkles className="w-3 h-3 text-teal-600" />
                Key Evidence Summary
              </h4>
              <ul className="space-y-1.5">
                {message.key_points.map((point, idx) => (
                  <li key={idx} className="text-xs text-slate-700 leading-relaxed flex items-start gap-2">
                    <span className="text-teal-600 font-bold text-xs mt-0.5">•</span>
                    <div className="flex-1">{formatKeyPointText(point)}</div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* When to seek care callout */}
          {message.when_to_seek_care && (
            <div className="my-2.5 bg-amber-50/80 border border-amber-200 rounded-xl p-3 text-xs text-amber-950 flex items-start gap-2.5 shadow-2xs">
              <AlertCircle className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
              <div className="space-y-0.5">
                <strong className="font-semibold block text-amber-900 text-xs">
                  When to Seek Medical Attention:
                </strong>
                <p className="leading-relaxed text-amber-900/90 text-xs">
                  {renderTextWithCitations(message.when_to_seek_care)}
                </p>
              </div>
            </div>
          )}

          {/* Compact Verified Sources Chips */}
          {message.sources && message.sources.length > 0 && (
            <div className="pt-1.5 flex flex-wrap items-center gap-1.5 text-xs">
              <span className="text-[11px] font-semibold text-slate-400 mr-1 flex items-center gap-1">
                <BookOpen className="w-3 h-3 text-slate-400" />
                Sources:
              </span>
              {message.sources.map((src, i) => (
                <button
                  key={i}
                  onClick={() => onCitationClick(src.citation_key, message.sources || [])}
                  className="inline-flex items-center gap-1 px-2.5 py-1 bg-white hover:bg-teal-50 border border-slate-200 hover:border-teal-300 rounded-lg text-xs font-medium text-slate-700 hover:text-teal-900 transition-all shadow-2xs group"
                >
                  <span className="text-[10px] font-bold text-teal-800 bg-teal-100 px-1 rounded">
                    {src.citation_key}
                  </span>
                  <span className="max-w-[160px] truncate group-hover:underline">
                    {src.source_name || src.title}
                  </span>
                  <ExternalLink className="w-2.5 h-2.5 text-slate-400 group-hover:text-teal-600" />
                </button>
              ))}
            </div>
          )}

          {/* Educational limitations disclaimer */}
          {message.limitations && (
            <div className="text-[11px] text-slate-400 italic pt-1">
              {message.limitations}
            </div>
          )}
        </div>

        {/* Minimal Action Toolbar (Listen, Copy, Feedback) */}
        <div className="flex items-center justify-between pt-1 border-t border-slate-100 text-xs text-slate-400">
          <div className="flex items-center gap-1">
            {/* Audio TTS */}
            <button
              onClick={handleToggleSpeech}
              className={`p-1.5 rounded-lg transition-colors flex items-center gap-1.5 text-xs ${
                isSpeaking
                  ? 'text-teal-800 bg-teal-100 font-medium'
                  : 'hover:text-slate-700 hover:bg-slate-100'
              }`}
              title={isSpeaking ? 'Stop listening' : 'Listen to answer'}
            >
              {isSpeaking ? (
                <>
                  <div className="flex items-center gap-0.5 h-3">
                    <span className="w-0.5 bg-teal-600 animate-wave-1 rounded-full" />
                    <span className="w-0.5 bg-teal-600 animate-wave-2 rounded-full" />
                    <span className="w-0.5 bg-teal-600 animate-wave-3 rounded-full" />
                    <span className="w-0.5 bg-teal-600 animate-wave-4 rounded-full" />
                  </div>
                  <span className="text-teal-700 font-medium text-[11px]">Playing</span>
                </>
              ) : (
                <>
                  <Volume2 className="w-3.5 h-3.5" />
                  <span className="text-[11px]">Listen</span>
                </>
              )}
            </button>

            {/* Copy Button */}
            <button
              onClick={handleCopy}
              className="p-1.5 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors flex items-center gap-1 text-xs"
              title="Copy answer to clipboard"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-teal-600" /> : <Copy className="w-3.5 h-3.5" />}
              <span className="text-[11px]">{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>

          {/* Feedback buttons */}
          <div className="flex items-center gap-0.5">
            <button
              onClick={() => onOpenFeedback(message.id)}
              className="p-1.5 hover:text-teal-700 hover:bg-slate-100 rounded-lg transition-colors"
              title="Helpful response"
            >
              <ThumbsUp className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onOpenFeedback(message.id)}
              className="p-1.5 hover:text-red-700 hover:bg-slate-100 rounded-lg transition-colors"
              title="Report inaccuracy"
            >
              <ThumbsDown className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
