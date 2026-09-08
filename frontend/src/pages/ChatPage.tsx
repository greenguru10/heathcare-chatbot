import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage, SourceCitation, SessionSummary } from '../types';
import {
  sendChatMessage,
  fetchSessions,
  fetchSessionDetail,
  renameSession,
  deleteSession,
  deleteAllSessions
} from '../api/client';
import { MessageBubble } from '../components/MessageBubble';
import { SourceDrawer } from '../components/SourceDrawer';
import { ChatSidebar } from '../components/ChatSidebar';
import {
  Send,
  Sparkles,
  Menu,
  Download,
  RotateCcw,
  ShieldCheck,
  CheckCircle2,
  FileText,
  Mic,
  MicOff,
  Activity,
  HeartPulse,
  Apple,
  Brain,
  Baby,
  ShieldAlert,
  Lock,
  ArrowRight
} from 'lucide-react';

interface ChatPageProps {
  onOpenFeedback: (answerId: string) => void;
}

interface CategoryStarter {
  category: string;
  icon: React.ElementType;
  prompt: string;
  subtitle: string;
  iconBg: string;
  iconColor: string;
}

const CATEGORY_PROMPTS: CategoryStarter[] = [
  {
    category: "Cardiovascular",
    icon: HeartPulse,
    prompt: "What is high blood pressure and how is it managed?",
    subtitle: "WHO Fact Sheet & Threshold Guidelines",
    iconBg: "bg-rose-50 border-rose-200",
    iconColor: "text-rose-600"
  },
  {
    category: "Nutrition & Diet",
    icon: Apple,
    prompt: "What are the core guidelines for a healthy diet according to WHO?",
    subtitle: "Nutrient balance & sodium guidelines",
    iconBg: "bg-emerald-50 border-emerald-200",
    iconColor: "text-emerald-600"
  },
  {
    category: "Metabolic Health",
    icon: Activity,
    prompt: "What are common symptoms and risk factors for diabetes?",
    subtitle: "Clinical screening & lifestyle measures",
    iconBg: "bg-teal-50 border-teal-200",
    iconColor: "text-teal-600"
  },
  {
    category: "Infectious & Fever",
    icon: ShieldAlert,
    prompt: "When is a fever in children or adults considered dangerous?",
    subtitle: "MedlinePlus Red-Flag Warning Signs",
    iconBg: "bg-amber-50 border-amber-200",
    iconColor: "text-amber-600"
  },
  {
    category: "Mental Health",
    icon: Brain,
    prompt: "What causes anxiety disorders and what coping strategies help?",
    subtitle: "NIH MedlinePlus Overview & Care",
    iconBg: "bg-indigo-50 border-indigo-200",
    iconColor: "text-indigo-600"
  },
  {
    category: "Maternal & Child",
    icon: Baby,
    prompt: "What are the essential nutrition guidelines for pregnant mothers?",
    subtitle: "ICMR & WHO Maternal Nutrition",
    iconBg: "bg-sky-50 border-sky-200",
    iconColor: "text-sky-600"
  }
];

export const ChatPage: React.FC<ChatPageProps> = ({ onOpenFeedback }) => {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [sessionId, setSessionId] = useState<string>(() => {
    return localStorage.getItem('active_health_session_id') || `session_${Date.now()}`;
  });
  const [sessionTitle, setSessionTitle] = useState<string>('New Health Consultation');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState<string>('Searching verified medical corpus...');
  const [region, setRegion] = useState<string>('en-IN');
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [isListening, setIsListening] = useState(false);

  // Source drawer state
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [activeSources, setActiveSources] = useState<SourceCitation[]>([]);
  const [highlightedKey, setHighlightedKey] = useState<string | undefined>(undefined);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Setup Web Speech API for voice dictation
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = region === 'en-IN' ? 'en-IN' : 'en-US';

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          setInput((prev) => (prev ? `${prev} ${transcript}` : transcript));
        }
        setIsListening(false);
      };

      recognition.onerror = () => setIsListening(false);
      recognition.onend = () => setIsListening(false);

      recognitionRef.current = recognition;
    }
  }, [region]);

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      alert('Voice dictation is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (e) {
        setIsListening(false);
      }
    }
  };

  // Load session list on mount
  const loadSessionList = async () => {
    try {
      const list = await fetchSessions();
      setSessions(list);
      return list;
    } catch (e) {
      console.warn('Could not load session list:', e);
      return [];
    }
  };

  // Load current session history
  const loadSessionHistory = async (targetId: string) => {
    try {
      const detail = await fetchSessionDetail(targetId);
      setSessionTitle(detail.title || 'Health Consultation');

      const reconstructed: ChatMessage[] = (detail.messages || []).map((m) => {
        const meta = m.metadata_json || {};
        return {
          id: m.id,
          role: m.role as any,
          content: m.content,
          response_mode: meta.response_mode,
          risk_level: meta.risk_level,
          key_points: meta.key_points,
          when_to_seek_care: meta.when_to_seek_care,
          limitations: meta.limitations,
          confidence: meta.confidence,
          sources: meta.sources,
          follow_up_suggestions: meta.follow_up_suggestions,
          created_at: m.created_at
        };
      });

      setMessages(reconstructed);
    } catch (e) {
      setMessages([]);
      setSessionTitle('New Health Consultation');
    }
  };

  useEffect(() => {
    loadSessionList();
    if (sessionId) {
      loadSessionHistory(sessionId);
      localStorage.setItem('active_health_session_id', sessionId);
    }
  }, [sessionId]);

  const handleSelectSession = (sId: string) => {
    setSessionId(sId);
  };

  const handleNewChat = () => {
    const newId = `session_${Date.now()}`;
    setSessionId(newId);
    setSessionTitle('New Health Consultation');
    setMessages([]);
    setDrawerOpen(false);
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  const handleRenameSession = async (sId: string, newTitle: string) => {
    try {
      await renameSession(sId, newTitle);
      if (sId === sessionId) {
        setSessionTitle(newTitle);
      }
      await loadSessionList();
    } catch (e) {
      console.error('Failed to rename session:', e);
    }
  };

  const handleDeleteSession = async (sId: string) => {
    try {
      await deleteSession(sId);
      const remaining = sessions.filter((s) => s.id !== sId);
      setSessions(remaining);
      if (sId === sessionId) {
        if (remaining.length > 0) {
          setSessionId(remaining[0].id);
        } else {
          handleNewChat();
        }
      }
    } catch (e) {
      console.error('Failed to delete session:', e);
    }
  };

  const handleClearAllSessions = async () => {
    try {
      await deleteAllSessions();
      setSessions([]);
      handleNewChat();
    } catch (e) {
      console.error('Failed to clear sessions:', e);
    }
  };

  const handleSend = async (queryText?: string) => {
    const textToSend = (queryText || input).trim();
    if (!textToSend || loading) return;

    setInput('');
    const userMsg: ChatMessage = {
      id: 'user_' + Date.now(),
      role: 'user',
      content: textToSend,
      created_at: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setLoadingStep('1. Checking safety guardrails & clinical boundaries...');

    const stepTimer1 = setTimeout(() => {
      setLoadingStep('2. Retrieving peer-reviewed sources (WHO, CDC, ICMR)...');
    }, 450);

    const stepTimer2 = setTimeout(() => {
      setLoadingStep('3. Synthesizing grounded response with citations...');
    }, 1200);

    try {
      const response = await sendChatMessage(textToSend, sessionId, region);

      const assistantMsg: ChatMessage = {
        id: response.request_id || 'asst_' + Date.now(),
        role: 'assistant',
        content: response.answer,
        response_mode: response.response_mode,
        risk_level: response.risk_level,
        key_points: response.key_points,
        when_to_seek_care: response.when_to_seek_care,
        limitations: response.limitations,
        confidence: response.confidence,
        sources: response.sources,
        follow_up_suggestions: response.follow_up_suggestions,
        created_at: new Date().toISOString()
      };

      setMessages((prev) => [...prev, assistantMsg]);
      loadSessionList();
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: 'err_' + Date.now(),
        role: 'assistant',
        content: `Notice: ${err.message || 'Unable to complete health assistant request.'}`,
        response_mode: 'insufficient_evidence',
        limitations: 'System encountered an error communicating with the health knowledge registry.',
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setLoading(false);
    }
  };

  const handleCitationClick = (key: string, sources: SourceCitation[]) => {
    setActiveSources(sources);
    setHighlightedKey(key);
    setDrawerOpen(true);
  };

  const handleExportChat = () => {
    if (messages.length === 0) return;
    let transcript = `# Health Consultation Summary - ${sessionTitle}\n`;
    transcript += `Date: ${new Date().toLocaleString()}\nJurisdiction: ${region}\n\n---\n\n`;

    messages.forEach((m) => {
      if (m.role === 'user') {
        transcript += `### User\n${m.content}\n\n`;
      } else {
        transcript += `### HealthEvidence Assistant (Grounded)\n${m.content}\n\n`;
        if (m.key_points && m.key_points.length > 0) {
          transcript += `**Key Evidence:**\n` + m.key_points.map((p) => `- ${p}`).join('\n') + '\n\n';
        }
        if (m.when_to_seek_care) {
          transcript += `**When to Seek Care:**\n${m.when_to_seek_care}\n\n`;
        }
        if (m.sources && m.sources.length > 0) {
          transcript += `**Sources:**\n` + m.sources.map((s) => `- [${s.citation_key}] ${s.title} (${s.source_name})`).join('\n') + '\n\n';
        }
      }
      transcript += `---\n\n`;
    });

    const blob = new Blob([transcript], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `health_consultation_${sessionId.slice(-6)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-full w-full flex overflow-hidden bg-[#f8fafc]">
      {/* Session History Sidebar */}
      <ChatSidebar
        sessions={sessions}
        activeSessionId={sessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onRenameSession={handleRenameSession}
        onDeleteSession={handleDeleteSession}
        onClearAllSessions={handleClearAllSessions}
        region={region}
        onRegionChange={setRegion}
        isOpenMobile={mobileSidebarOpen}
        onCloseMobile={() => setMobileSidebarOpen(false)}
      />

      {/* Main Chat Workspace */}
      <main className="flex-1 flex flex-col h-full min-w-0 bg-[#f8fafc] overflow-hidden">
        {/* Workspace Top Header Bar */}
        <header className="h-12 flex-shrink-0 bg-white border-b border-slate-200 px-4 sm:px-6 flex items-center justify-between z-10 shadow-2xs">
          <div className="flex items-center gap-2.5 min-w-0">
            <button
              onClick={() => setMobileSidebarOpen(true)}
              className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg md:hidden transition-colors"
              title="Open history sidebar"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2 truncate">
              <span className="w-2 h-2 rounded-full bg-emerald-500 flex-shrink-0" />
              <h2 className="text-xs font-bold text-slate-800 truncate" title={sessionTitle}>
                {sessionTitle}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <>
                <button
                  onClick={handleExportChat}
                  className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-teal-800 bg-slate-50 hover:bg-slate-100 px-3 py-1 rounded-lg border border-slate-200 transition-all shadow-2xs font-medium"
                  title="Export conversation as Markdown"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Export</span>
                </button>
                <button
                  onClick={handleNewChat}
                  className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-teal-800 bg-slate-50 hover:bg-slate-100 px-3 py-1 rounded-lg border border-slate-200 transition-all shadow-2xs font-medium"
                  title="Start fresh consultation"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Reset</span>
                </button>
              </>
            )}
          </div>
        </header>

        {/* Messages Scroll Area */}
        <div className="flex-1 min-h-0 overflow-y-auto px-4 sm:px-6 py-5 scroll-smooth">
          <div className="max-w-4xl mx-auto w-full space-y-4 pb-8">
            {messages.length === 0 ? (
              <div className="py-4 px-2 animate-in fade-in duration-200">
                {/* Friendly Welcome Header */}
                <div className="text-center mb-6">
                  <div className="w-12 h-12 rounded-2xl bg-teal-100 text-teal-800 flex items-center justify-center mx-auto mb-2.5 shadow-2xs">
                    <Sparkles className="w-6 h-6 text-teal-700" />
                  </div>

                  <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight font-display">
                    Hello! How can I help with your health questions?
                  </h2>
                  <p className="text-xs sm:text-sm text-slate-600 mt-1.5 leading-relaxed max-w-lg mx-auto">
                    Ask educational questions about symptoms, disease prevention, nutrition, vaccines, or medications. All answers are grounded in verified medical publications.
                  </p>
                </div>

                {/* Categorized Interactive Prompt Grid (3 columns on desktop to fit without scroll) */}
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 mb-5">
                  {CATEGORY_PROMPTS.map((item, idx) => {
                    const Icon = item.icon;
                    return (
                      <button
                        key={idx}
                        onClick={() => handleSend(item.prompt)}
                        className="bg-white hover:bg-teal-50/50 border border-slate-200 hover:border-teal-300 p-3 rounded-xl text-left transition-all duration-150 group shadow-2xs hover:shadow-xs flex flex-col justify-between"
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <div className="flex items-center gap-1.5">
                            <div className={`w-6 h-6 rounded-lg border flex items-center justify-center ${item.iconBg} ${item.iconColor}`}>
                              <Icon className="w-3.5 h-3.5" />
                            </div>
                            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                              {item.category}
                            </span>
                          </div>
                          <ArrowRight className="w-3 h-3 text-slate-400 group-hover:text-teal-700 group-hover:translate-x-0.5 transition-all" />
                        </div>
                        <p className="text-xs font-semibold text-slate-800 group-hover:text-teal-950 leading-snug line-clamp-2">
                          "{item.prompt}"
                        </p>
                        <span className="text-[10.5px] text-slate-400 mt-1.5 block font-normal truncate">
                          {item.subtitle}
                        </span>
                      </button>
                    );
                  })}
                </div>

                {/* Trust Badges */}
                <div className="bg-white rounded-xl p-3 flex flex-wrap justify-around items-center gap-2 text-xs text-slate-600 border border-slate-200 shadow-2xs">
                  <div className="flex items-center gap-1.5 font-medium text-[11px]">
                    <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
                    <span>Deterministic Safety Triage</span>
                  </div>
                  <div className="flex items-center gap-1.5 font-medium text-[11px]">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    <span>100% Inline Citations</span>
                  </div>
                  <div className="flex items-center gap-1.5 font-medium text-[11px]">
                    <FileText className="w-3.5 h-3.5 text-sky-600" />
                    <span>Peer-Reviewed Corpus</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((msg) => (
                  <MessageBubble
                    key={msg.id}
                    message={msg}
                    onCitationClick={handleCitationClick}
                    onOpenFeedback={onOpenFeedback}
                  />
                ))}

                {/* Follow-up suggestion pills on the latest message */}
                {messages.length > 0 &&
                  messages[messages.length - 1].role === 'assistant' &&
                  messages[messages.length - 1].follow_up_suggestions && (
                    <div className="flex flex-wrap items-center gap-2 ml-11 mt-3 animate-in fade-in slide-in-from-left-1">
                      <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-0.5">
                        Suggested:
                      </span>
                      {messages[messages.length - 1].follow_up_suggestions!.map((suggestion, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSend(suggestion)}
                          className="text-xs font-semibold text-teal-900 bg-white hover:bg-teal-50 border border-teal-200 hover:border-teal-400 px-3.5 py-1.5 rounded-full transition-all shadow-2xs hover:shadow-xs active:scale-95"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}

                {/* Step-by-Step Retrieval Indicator */}
                {loading && (
                  <div className="flex items-center gap-3 my-3 ml-11 bg-white border border-teal-200/90 px-4 py-2.5 rounded-2xl shadow-2xs text-xs text-teal-900 animate-in fade-in">
                    <div className="w-4 h-4 border-2 border-teal-600 border-t-transparent rounded-full animate-spin flex-shrink-0" />
                    <span className="font-medium tracking-wide">{loadingStep}</span>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Clean Fixed Bottom Input Bar */}
        <div className="flex-shrink-0 bg-white border-t border-slate-200 px-4 sm:px-6 py-3 z-10 shadow-xs">
          <div className="max-w-3xl mx-auto w-full">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="bg-white border border-slate-300 hover:border-slate-400 focus-within:!border-teal-600 focus-within:ring-4 focus-within:ring-teal-500/10 rounded-2xl p-1.5 shadow-xs transition-all flex items-center gap-2"
            >
              {/* Voice Dictation Button */}
              <button
                type="button"
                onClick={toggleVoiceInput}
                className={`p-2.5 rounded-xl transition-all flex-shrink-0 ${
                  isListening
                    ? 'bg-red-600 text-white animate-pulse shadow-md shadow-red-600/20'
                    : 'text-slate-400 hover:text-teal-700 hover:bg-slate-100'
                }`}
                title={isListening ? 'Listening... click to stop' : 'Dictate question with voice'}
              >
                {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </button>

              {/* Main Text Input */}
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask an educational health question (e.g., What are the symptoms of high blood pressure?)..."
                disabled={loading}
                className="flex-1 bg-transparent px-2 py-1.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none"
              />

              {/* Send Button */}
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="w-9 h-9 bg-teal-700 hover:bg-teal-800 disabled:opacity-30 disabled:hover:bg-teal-700 text-white font-bold rounded-xl shadow-xs transition-all flex-shrink-0 active:scale-95 cursor-pointer flex items-center justify-center"
                title="Send question"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>

            {/* Privacy Footnote */}
            <div className="flex items-center justify-center gap-1.5 text-[10.5px] text-slate-400 mt-2">
              <Lock className="w-3 h-3 text-slate-400" />
              <span>Health literacy only &bull; Zero clinical prescription &bull; Do not submit personal health identifiers</span>
            </div>
          </div>
        </div>
      </main>

      {/* Sliding Source Excerpt Drawer */}
      <SourceDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        sources={activeSources}
        highlightedKey={highlightedKey}
      />
    </div>
  );
};
