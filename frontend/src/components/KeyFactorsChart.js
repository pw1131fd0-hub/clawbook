import React from 'react';

export default function KeyFactorsChart({ factors = [] }) {
  if (!factors || factors.length === 0) {
    return null;
  }

  // Sort factors by importance descending
  const sortedFactors = [...factors].sort((a, b) => {
    const weightA = a.weight || a.importance || 0;
    const weightB = b.weight || b.importance || 0;
    return weightB - weightA;
  });

  const maxWeight = Math.max(...sortedFactors.map(f => f.weight || f.importance || 0));

  return (
    <div>
      <p className="text-sm text-slate-400 dark:text-slate-400 font-semibold mb-4">KEY FACTORS</p>
      <div className="space-y-4">
        {sortedFactors.map((factor, index) => {
          const weight = factor.weight || factor.importance || 0;
          const percentage = (weight / maxWeight) * 100;

          return (
            <div key={index}>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-slate-200 dark:text-slate-200 font-medium">
                  {factor.name}
                </span>
                <span className="text-xs text-slate-400 dark:text-slate-400">
                  {(weight * 100).toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-slate-700 dark:bg-slate-700 rounded-full h-2.5">
                <div
                  className="bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-600 dark:to-cyan-600 h-2.5 rounded-full transition-all"
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
              {factor.description && (
                <p className="text-xs text-slate-500 dark:text-slate-500 mt-1">
                  {factor.description}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
