import React from 'react';

export default function ConfidenceIndicator({ confidence = 0.5, rationale = '' }) {
  const percentage = Math.round(confidence * 100);

  // Determine color based on confidence level
  let bgColor = 'bg-red-600 dark:bg-red-600';
  let textColor = 'text-red-200 dark:text-red-200';
  let label = 'Low Confidence';

  if (confidence >= 0.8) {
    bgColor = 'bg-green-600 dark:bg-green-600';
    textColor = 'text-green-200 dark:text-green-200';
    label = 'High Confidence';
  } else if (confidence >= 0.6) {
    bgColor = 'bg-yellow-600 dark:bg-yellow-600';
    textColor = 'text-yellow-200 dark:text-yellow-200';
    label = 'Medium Confidence';
  }

  return (
    <div className="p-4 bg-slate-800 dark:bg-slate-800 rounded-lg border border-slate-700 dark:border-slate-700">
      <p className="text-sm text-slate-400 dark:text-slate-400 font-semibold mb-3">CONFIDENCE LEVEL</p>

      <div className="mb-3">
        <div className="flex justify-between mb-2">
          <span className={`text-sm font-bold ${textColor}`}>{label}</span>
          <span className="text-sm font-bold text-slate-200 dark:text-slate-200">{percentage}%</span>
        </div>
        <div className="w-full bg-slate-700 dark:bg-slate-700 rounded-full h-3">
          <div
            className={`${bgColor} h-3 rounded-full transition-all duration-500`}
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
      </div>

      {rationale && (
        <p className="text-sm text-slate-300 dark:text-slate-300 leading-relaxed">
          {rationale}
        </p>
      )}
    </div>
  );
}
