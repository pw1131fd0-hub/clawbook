import React from 'react';
import PropTypes from 'prop-types';

export default function ReasoningTimeline({ steps = [] }) {
  if (!steps || steps.length === 0) {
    return null;
  }

  return (
    <div>
      <p className="text-sm text-slate-400 font-semibold mb-4">REASONING STEPS</p>
      <div className="relative">
        {steps.map((step, index) => {
          const stepKey = step.id || step.step_number || index;
          return (
            <div key={stepKey} className="mb-6 last:mb-0">
              <div className="flex gap-4">
                {/* Timeline indicator */}
                <div className="flex flex-col items-center">
                  <div className="w-8 h-8 rounded-full bg-blue-600 border-2 border-slate-700 flex items-center justify-center">
                    <span className="text-white text-xs font-bold">{index + 1}</span>
                  </div>
                  {index < steps.length - 1 && (
                    <div className="w-0.5 h-12 bg-slate-700 mt-2"></div>
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 pb-2">
                  <p className="text-sm font-semibold text-slate-200 mb-1">
                    {step.step_number}. {step.description}
                  </p>
                  {step.reasoning && (
                    <p className="text-sm text-slate-400 leading-relaxed">
                      {step.reasoning}
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

ReasoningTimeline.propTypes = {
  steps: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      step_number: PropTypes.number,
      description: PropTypes.string.isRequired,
      reasoning: PropTypes.string,
    })
  ),
};
