import React, { useState } from 'react';
import { AlertCircle, X, ShieldAlert, PhoneCall } from 'lucide-react';

export const SafetyBanner: React.FC = () => {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <div className="bg-amber-50/90 border-b border-amber-200/90 px-4 py-2 text-xs text-amber-900 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 min-w-0">
          <ShieldAlert className="w-4 h-4 text-amber-600 flex-shrink-0" />
          <span className="truncate">
            <strong className="font-semibold text-amber-950">Educational Health Information:</strong> Not a diagnostic or prescribing tool. In case of emergency, call local emergency services immediately.
          </span>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <span className="hidden sm:inline-flex items-center gap-1 font-bold text-[11px] text-amber-900 bg-amber-100/90 px-2.5 py-0.5 rounded-full border border-amber-300">
            <PhoneCall className="w-3 h-3 text-amber-700" />
            112 (IN) / 911 (US) / 999 (UK)
          </span>
          <button
            onClick={() => setDismissed(true)}
            className="text-amber-700 hover:text-amber-950 p-0.5 rounded-lg hover:bg-amber-100 transition-colors"
            title="Dismiss notice"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
