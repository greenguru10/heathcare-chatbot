import React from 'react';

interface CitationBadgeProps {
  citationKey: string;
  sourceTitle?: string;
  sourcePublisher?: string;
  onClick: (key: string) => void;
}

export const CitationBadge: React.FC<CitationBadgeProps> = ({
  citationKey,
  sourceTitle,
  sourcePublisher,
  onClick
}) => {
  const tooltipText = sourceTitle
    ? `[${citationKey}] ${sourceTitle} (${sourcePublisher || 'Verified Source'}) - Click to view excerpt`
    : `View verified source details for [${citationKey}]`;

  return (
    <button
      onClick={(e) => {
        e.stopPropagation();
        onClick(citationKey);
      }}
      className="inline-flex items-center justify-center mx-1 px-1.5 py-0.5 text-[11px] font-bold text-teal-900 bg-teal-100 hover:bg-teal-200 active:bg-teal-300 border border-teal-300/80 rounded-md transition-all hover:scale-105 active:scale-95 shadow-2xs cursor-pointer align-baseline"
      title={tooltipText}
    >
      [{citationKey}]
    </button>
  );
};
