import React from 'react';
import PropTypes from 'prop-types';

// Constants for factor weight defaults
const DEFAULT_WEIGHT = 0;
const WEIGHT_MULTIPLIER = 100;

function getFactorWeight(factor) {
  return factor.weight || factor.importance || DEFAULT_WEIGHT;
}

export default function KeyFactorsChart({ factors = [] }) {
  if (!factors || factors.length === 0) {
    return null;
  }

  // Sort factors by importance descending
  const sortedFactors = [...factors].sort((a, b) => {
    const weightA = getFactorWeight(a);
    const weightB = getFactorWeight(b);
    return weightB - weightA;
  });

  const maxWeight = Math.max(...sortedFactors.map(getFactorWeight));

  return (
    <div>
      <p className="text-sm text-slate-400 font-semibold mb-4">KEY FACTORS</p>
      <div className="space-y-4">
        {sortedFactors.map((factor) => {
          const factorKey = factor.id || factor.name;
          const weight = getFactorWeight(factor);
          const percentage = (weight / maxWeight) * WEIGHT_MULTIPLIER;

          return (
            <div key={factorKey}>
              <div className="flex justify-between mb-1">
                <span className="text-sm text-slate-200 font-medium">
                  {factor.name}
                </span>
                <span className="text-xs text-slate-400">
                  {(weight * WEIGHT_MULTIPLIER).toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2.5">
                <div
                  className="bg-gradient-to-r from-blue-600 to-cyan-600 h-2.5 rounded-full transition-all"
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
              {factor.description && (
                <p className="text-xs text-slate-500 mt-1">
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

KeyFactorsChart.propTypes = {
  factors: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      name: PropTypes.string.isRequired,
      weight: PropTypes.number,
      importance: PropTypes.number,
      description: PropTypes.string,
    })
  ),
};
