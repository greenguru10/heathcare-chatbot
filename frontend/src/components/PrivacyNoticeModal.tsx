import React from 'react';
import { X, Shield, Lock, AlertTriangle, FileText, Check } from 'lucide-react';

interface PrivacyNoticeModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PrivacyNoticeModal: React.FC<PrivacyNoticeModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200 animate-in zoom-in-95 duration-150 max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2 text-teal-800">
            <Shield className="w-5 h-5" />
            <h3 className="font-bold text-slate-900 text-base">Safety Boundary & Privacy Principles</h3>
          </div>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-700 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-4 space-y-4 text-xs text-slate-700 leading-relaxed">
          <div className="bg-teal-50 border border-teal-200 rounded-xl p-3.5">
            <h4 className="font-bold text-teal-950 mb-1 flex items-center gap-1.5">
              <Check className="w-4 h-4 text-teal-700" />
              1. Educational Health Literacy Only
            </h4>
            <p>
              This system provides source-grounded educational information from verified medical authorities (WHO, CDC, MedlinePlus, ICMR). It does not provide medical diagnoses, clinical triage, or prescriptive advice.
            </p>
          </div>

          <div className="bg-red-50 border border-red-200 rounded-xl p-3.5 text-red-950">
            <h4 className="font-bold text-red-900 mb-1 flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4 text-red-600" />
              2. Zero Emergency or Crisis Triage
            </h4>
            <p>
              Severe symptoms (chest pain, breathing difficulty, poisoning, acute trauma, self-harm) trigger immediate emergency directions. Always contact <strong>112 (India) / 911 / 999</strong> for urgent care.
            </p>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5">
            <h4 className="font-bold text-slate-900 mb-1 flex items-center gap-1.5">
              <Lock className="w-4 h-4 text-slate-700" />
              3. Data Minimization & Privacy Protection
            </h4>
            <ul className="list-disc list-inside space-y-1 mt-1 text-slate-600">
              <li>Do not enter personal identifiers (names, Aadhaar/SSN, contact numbers).</li>
              <li>PII is stripped and redacted automatically.</li>
              <li>Sessions can be deleted at any time from the chat sidebar.</li>
              <li>User conversations are never used to train machine learning models.</li>
            </ul>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 text-xs font-semibold text-white bg-teal-700 hover:bg-teal-800 rounded-xl shadow-sm transition-all"
          >
            I Understand
          </button>
        </div>
      </div>
    </div>
  );
};
