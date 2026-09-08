import React, { useState } from 'react';
import { SessionSummary } from '../types';
import {
  Plus,
  MessageSquare,
  Trash2,
  Edit2,
  Check,
  X,
  Clock,
  ShieldCheck,
  Globe
} from 'lucide-react';

interface ChatSidebarProps {
  sessions: SessionSummary[];
  activeSessionId: string;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
  onRenameSession: (sessionId: string, newTitle: string) => Promise<void>;
  onDeleteSession: (sessionId: string) => Promise<void>;
  onClearAllSessions: () => Promise<void>;
  region: string;
  onRegionChange: (region: string) => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onRenameSession,
  onDeleteSession,
  onClearAllSessions,
  region,
  onRegionChange,
  isOpenMobile,
  onCloseMobile
}) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  // Group sessions by date
  const groupSessions = (list: SessionSummary[]) => {
    const today: SessionSummary[] = [];
    const yesterday: SessionSummary[] = [];
    const lastWeek: SessionSummary[] = [];
    const older: SessionSummary[] = [];

    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const yesterdayStart = todayStart - 86400000;
    const weekStart = todayStart - 7 * 86400000;

    list.forEach((s) => {
      const updatedTime = new Date(s.updated_at || s.created_at).getTime();
      if (updatedTime >= todayStart) {
        today.push(s);
      } else if (updatedTime >= yesterdayStart) {
        yesterday.push(s);
      } else if (updatedTime >= weekStart) {
        lastWeek.push(s);
      } else {
        older.push(s);
      }
    });

    return { today, yesterday, lastWeek, older };
  };

  const { today, yesterday, lastWeek, older } = groupSessions(sessions);

  const startEditing = (s: SessionSummary, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(s.id);
    setEditTitle(s.title);
  };

  const saveEditing = async (e: React.MouseEvent | React.FormEvent) => {
    e.stopPropagation();
    if (editingId && editTitle.trim()) {
      await onRenameSession(editingId, editTitle.trim());
    }
    setEditingId(null);
  };

  const cancelEditing = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(null);
  };

  const handleDelete = async (sId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('Delete this conversation history?')) {
      await onDeleteSession(sId);
    }
  };

  const renderSessionItem = (s: SessionSummary) => {
    const isActive = s.id === activeSessionId;
    const isEditing = s.id === editingId;

    return (
      <div
        key={s.id}
        onClick={() => {
          if (!isEditing) {
            onSelectSession(s.id);
            onCloseMobile();
          }
        }}
        className={`group relative flex items-center justify-between gap-2 px-3 py-2 rounded-xl cursor-pointer text-xs transition-all ${
          isActive
            ? 'bg-teal-50 text-teal-900 border border-teal-200/90 font-semibold shadow-2xs'
            : 'text-slate-700 hover:bg-slate-200/60 hover:text-slate-900 border border-transparent'
        }`}
      >
        <div className="flex items-center gap-2.5 min-w-0 flex-1">
          <MessageSquare
            className={`w-3.5 h-3.5 flex-shrink-0 ${
              isActive ? 'text-teal-700' : 'text-slate-400 group-hover:text-slate-600'
            }`}
          />
          {isEditing ? (
            <div className="flex items-center gap-1 flex-1 min-w-0" onClick={(e) => e.stopPropagation()}>
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') saveEditing(e);
                  if (e.key === 'Escape') setEditingId(null);
                }}
                autoFocus
                className="w-full bg-white border border-teal-600 rounded px-1.5 py-0.5 text-xs text-slate-900 focus:outline-none shadow-2xs"
              />
              <button onClick={saveEditing} className="p-1 hover:text-teal-700 text-slate-500">
                <Check className="w-3 h-3" />
              </button>
              <button onClick={cancelEditing} className="p-1 hover:text-red-600 text-slate-400">
                <X className="w-3 h-3" />
              </button>
            </div>
          ) : (
            <span className="truncate flex-1 text-[12.5px] leading-tight" title={s.title}>
              {s.title}
            </span>
          )}
        </div>

        {!isEditing && (
          <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={(e) => startEditing(s, e)}
              className="p-1 hover:text-teal-700 text-slate-400 hover:bg-white rounded"
              title="Rename conversation"
            >
              <Edit2 className="w-3 h-3" />
            </button>
            <button
              onClick={(e) => handleDelete(s.id, e)}
              className="p-1 hover:text-red-600 text-slate-400 hover:bg-white rounded"
              title="Delete conversation"
            >
              <Trash2 className="w-3 h-3" />
            </button>
          </div>
        )}
      </div>
    );
  };

  const renderSection = (title: string, list: SessionSummary[]) => {
    if (list.length === 0) return null;
    return (
      <div className="mb-3.5">
        <h5 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 px-3 mb-1 flex items-center gap-1.5">
          <Clock className="w-3 h-3" />
          {title}
        </h5>
        <div className="space-y-0.5">{list.map(renderSessionItem)}</div>
      </div>
    );
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-slate-50 text-slate-800 border-r border-slate-200">
      {/* Top Header & New Chat Button */}
      <div className="p-3.5 border-b border-slate-200 space-y-3">
        <button
          onClick={() => {
            onNewChat();
            onCloseMobile();
          }}
          className="w-full flex items-center justify-center gap-2 bg-teal-700 hover:bg-teal-800 text-white text-xs font-semibold py-2.5 px-4 rounded-xl shadow-xs hover:shadow-sm transition-all active:scale-[0.98]"
        >
          <Plus className="w-4 h-4" />
          <span>New Consultation</span>
        </button>

        {/* Region Selector */}
        <div>
          <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center justify-between">
            <span className="flex items-center gap-1">
              <Globe className="w-3 h-3" />
              Regional Health Context
            </span>
          </label>
          <select
            value={region}
            onChange={(e) => onRegionChange(e.target.value)}
            className="w-full text-xs bg-white border border-slate-200 rounded-lg p-2 text-slate-800 focus:outline-none focus:border-teal-600 shadow-2xs transition-colors font-medium"
          >
            <option value="en-IN">🇮🇳 India (MoHFW / ICMR / 112)</option>
            <option value="en-US">🇺🇸 USA (CDC / MedlinePlus / 911)</option>
            <option value="en-GB">🇬🇧 UK (NHS / NICE / 999)</option>
          </select>
        </div>
      </div>

      {/* Session History Scroll List */}
      <div className="flex-1 overflow-y-auto p-2.5 space-y-1">
        {sessions.length === 0 ? (
          <div className="text-center py-10 px-2 text-slate-400">
            <MessageSquare className="w-6 h-6 mx-auto mb-2 opacity-40 text-slate-400" />
            <p className="text-xs font-medium text-slate-500">No previous sessions</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Start a new consultation above</p>
          </div>
        ) : (
          <>
            {renderSection('Today', today)}
            {renderSection('Yesterday', yesterday)}
            {renderSection('Previous 7 Days', lastWeek)}
            {renderSection('Older', older)}
          </>
        )}
      </div>

      {/* Footer Notice & Clear */}
      <div className="p-3 border-t border-slate-200 text-[11px] bg-slate-100/70 space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-teal-800 font-semibold text-xs">
            <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
            <span>Curated Sources Only</span>
          </div>
          {sessions.length > 0 && (
            <button
              onClick={() => setShowClearConfirm(true)}
              className="text-[10.5px] text-slate-500 hover:text-red-600 transition-colors"
              title="Clear all session history"
            >
              Clear all
            </button>
          )}
        </div>

        <p className="text-[10.5px] text-slate-500 leading-snug">
          Answers grounded exclusively in peer-reviewed WHO, CDC, MedlinePlus & ICMR health registries.
        </p>

        {showClearConfirm && (
          <div className="p-2 bg-red-50 border border-red-200 rounded-lg text-xs text-red-900 space-y-1.5 animate-in fade-in">
            <p className="text-[11px]">Clear all conversational history?</p>
            <div className="flex justify-end gap-1.5">
              <button
                onClick={() => setShowClearConfirm(false)}
                className="px-2 py-0.5 bg-white text-[10.5px] rounded text-slate-700 hover:bg-slate-100 border border-slate-200"
              >
                Cancel
              </button>
              <button
                onClick={async () => {
                  await onClearAllSessions();
                  setShowClearConfirm(false);
                }}
                className="px-2 py-0.5 bg-red-600 text-[10.5px] rounded text-white font-medium hover:bg-red-700"
              >
                Confirm
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <aside className="w-68 flex-shrink-0 hidden md:flex flex-col h-full">
        {sidebarContent}
      </aside>

      {/* Mobile Slide-Over Sidebar */}
      {isOpenMobile && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs" onClick={onCloseMobile} />
          <div className="relative w-72 max-w-full h-full shadow-xl z-10 animate-in slide-in-from-left duration-200">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
};
