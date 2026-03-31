import React, { useState, useEffect } from 'react';
import ReasoningTimeline from './ReasoningTimeline';
import CandidateComparison from './CandidateComparison';
import ConfidenceIndicator from './ConfidenceIndicator';
import KeyFactorsChart from './KeyFactorsChart';
import { fetchDecisionPath } from '../utils/api';

export default function DecisionPathViewer({ postId }) {
  const [decisionPath, setDecisionPath] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDecisionPath();
  }, [postId]);

  const loadDecisionPath = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDecisionPath(postId);
      setDecisionPath(data);
    } catch (err) {
      // Decision path might not exist, which is fine
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="mt-6 p-4 bg-slate-800 dark:bg-slate-800 rounded-lg border border-slate-700 dark:border-slate-700">
        <div className="text-slate-400 dark:text-slate-400">Loading decision path...</div>
      </div>
    );
  }

  if (error || !decisionPath) {
    return null; // Decision path not available, don't show section
  }

  return (
    <div className="mt-6 border-t border-slate-800 dark:border-slate-700 pt-6">
      <h3 className="text-xl font-bold text-slate-100 dark:text-slate-100 mb-4">AI Decision Path</h3>

      {/* Confidence Indicator */}
      <div className="mb-6">
        <ConfidenceIndicator
          confidence={decisionPath.final_decision.confidence}
          rationale={decisionPath.final_decision.rationale}
        />
      </div>

      {/* Final Decision */}
      <div className="mb-6 p-4 bg-slate-800 dark:bg-slate-800 rounded-lg border border-slate-700 dark:border-slate-700">
        <p className="text-sm text-slate-400 dark:text-slate-400 font-semibold mb-2">FINAL DECISION</p>
        <p className="text-slate-100 dark:text-slate-100 text-lg font-semibold">
          {decisionPath.final_decision.decision}
        </p>
      </div>

      {/* Key Factors Chart */}
      {decisionPath.key_factors && decisionPath.key_factors.length > 0 && (
        <div className="mb-6">
          <KeyFactorsChart factors={decisionPath.key_factors} />
        </div>
      )}

      {/* Reasoning Timeline */}
      {decisionPath.reasoning_steps && decisionPath.reasoning_steps.length > 0 && (
        <div className="mb-6">
          <ReasoningTimeline steps={decisionPath.reasoning_steps} />
        </div>
      )}

      {/* Candidate Comparison */}
      {decisionPath.candidates && decisionPath.candidates.length > 1 && (
        <div className="mb-6">
          <CandidateComparison candidates={decisionPath.candidates} />
        </div>
      )}

      {/* Metadata */}
      <div className="mt-6 p-4 bg-slate-800/50 dark:bg-slate-800/50 rounded-lg border border-slate-700 dark:border-slate-700">
        <div className="flex gap-4 text-xs text-slate-500 dark:text-slate-500">
          {decisionPath.model_used && (
            <span>Model: {decisionPath.model_used}</span>
          )}
          {decisionPath.decision_time_ms && (
            <span>Decision Time: {decisionPath.decision_time_ms}ms</span>
          )}
        </div>
      </div>
    </div>
  );
}
