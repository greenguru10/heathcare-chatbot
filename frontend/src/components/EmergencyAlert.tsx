import React from 'react';
import { AlertOctagon, PhoneCall, ShieldAlert } from 'lucide-react';

interface EmergencyAlertProps {
  answerText: string;
}

export const EmergencyAlert: React.FC<EmergencyAlertProps> = ({ answerText }) => {
  return (
    <div className="bg-red-50 border-2 border-red-500/80 rounded-2xl p-5 my-3 shadow-lg shadow-red-500/10 text-red-950">
      <div className="flex items-start gap-4">
        <div className="p-2.5 bg-red-600 text-white rounded-xl shadow-md flex-shrink-0">
          <AlertOctagon className="w-6 h-6 animate-pulse" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1.5">
            <h3 className="text-base font-bold text-red-900 tracking-tight">Immediate Medical Emergency Notice</h3>
            <span className="text-[10px] uppercase font-extrabold tracking-wider bg-red-200 text-red-900 px-2 py-0.5 rounded-full">
              Urgent Action Required
            </span>
          </div>
          <div className="text-sm leading-relaxed text-red-900 whitespace-pre-line font-medium">
            {answerText}
          </div>
          <div className="mt-4 pt-3 border-t border-red-200 flex flex-wrap items-center gap-4 text-xs font-semibold text-red-800">
            <div className="flex items-center gap-1.5 bg-white px-3 py-1.5 rounded-lg border border-red-300 shadow-sm">
              <PhoneCall className="w-4 h-4 text-red-600" />
              <span>India Emergency: <strong>112 / 108</strong></span>
            </div>
            <div className="flex items-center gap-1.5 bg-white px-3 py-1.5 rounded-lg border border-red-300 shadow-sm">
              <PhoneCall className="w-4 h-4 text-red-600" />
              <span>US Emergency: <strong>911</strong></span>
            </div>
            <div className="flex items-center gap-1.5 bg-white px-3 py-1.5 rounded-lg border border-red-300 shadow-sm">
              <PhoneCall className="w-4 h-4 text-red-600" />
              <span>UK Emergency: <strong>999</strong></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
