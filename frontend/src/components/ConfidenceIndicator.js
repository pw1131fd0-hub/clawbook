import React from 'react';
import PropTypes from 'prop-types';

// Confidence threshold constants
const CONFIDENCE_THRESHOLDS = {
  HIGH: 0.8,
  MEDIUM: 0.6,
};

const CONFIDENCE_STYLES = {
  high: {
    bgColor: 'bg-green-600',
    textColor: 'text-green-200',
    label: 'High Confidence',
  },
  medium: {
    bgColor: 'bg-yellow-600',
    textColor: 'text-yellow-200',
    label: 'Medium Confidence',
  },
  low: {
    bgColor: 'bg-red-600',
    textColor: 'text-red-200',
    label: 'Low Confidence',
  },
};

function getConfidenceLevel(confidence) {
  if (confidence >= CONFIDENCE_THRESHOLDS.HIGH) return CONFIDENCE_STYLES.high;
  if (confidence >= CONFIDENCE_THRESHOLDS.MEDIUM) return CONFIDENCE_STYLES.medium;
  return CONFIDENCE_STYLES.low;
}

export default function ConfidenceIndicator({ confidence = 0.5, rationale = '' }) {
  const percentage = Math.round(confidence * 100);
  const { bgColor, textColor, label } = getConfidenceLevel(confidence);

  return (
    <div className="p-4 bg-slate-800 rounded-lg border border-slate-700">
      <p className="text-sm text-slate-400 font-semibold mb-3">CONFIDENCE LEVEL</p>

      <div className="mb-3">
        <div className="flex justify-between mb-2">
          <span className={`text-sm font-bold ${textColor}`}>{label}</span>
          <span className="text-sm font-bold text-slate-200">{percentage}%</span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-3">
          <div
            className={`${bgColor} h-3 rounded-full transition-all duration-500`}
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
      </div>

      {rationale && (
        <p className="text-sm text-slate-300 leading-relaxed">
          {rationale}
        </p>
      )}
    </div>
  );
}

ConfidenceIndicator.propTypes = {
  confidence: PropTypes.number,
  rationale: PropTypes.string,
};
