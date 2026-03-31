import React, { useState } from 'react';
import PropTypes from 'prop-types';

// Sort constants
const SORT_OPTIONS = {
  RANK: 'rank',
  SCORE: 'score',
};

export default function CandidateComparison({ candidates = [] }) {
  const [sortBy, setSortBy] = useState(SORT_OPTIONS.RANK);

  if (!candidates || candidates.length === 0) {
    return null;
  }

  const sortedCandidates = [...candidates].sort((a, b) => {
    if (sortBy === SORT_OPTIONS.RANK) {
      return a.rank - b.rank;
    }
    if (sortBy === SORT_OPTIONS.SCORE) {
      return b.feasibility_score - a.feasibility_score;
    }
    return 0;
  });

  const maxScore = Math.max(...candidates.map(c => c.feasibility_score || 0));

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-slate-400 font-semibold">CANDIDATES CONSIDERED</p>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-3 py-1 bg-slate-800 border border-slate-700 rounded text-xs text-slate-200"
        >
          <option value={SORT_OPTIONS.RANK}>Sort by Rank</option>
          <option value={SORT_OPTIONS.SCORE}>Sort by Score</option>
        </select>
      </div>

      <div className="space-y-3">
        {sortedCandidates.map((candidate) => {
          const candidateKey = candidate.id || candidate.rank || candidate.option;
          return (
            <div
              key={candidateKey}
              className="p-4 bg-slate-800 rounded-lg border border-slate-700"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="font-semibold text-slate-100">
                    #{candidate.rank} - {candidate.option}
                  </p>
                  {candidate.description && (
                    <p className="text-sm text-slate-400 mt-1">
                      {candidate.description}
                    </p>
                  )}
                </div>
                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                  candidate.rank === 1
                    ? 'bg-green-600 text-white'
                    : 'bg-slate-700 text-slate-200'
                }`}>
                  {candidate.rank === 1 ? 'Selected' : `Rank #${candidate.rank}`}
                </span>
              </div>

              {/* Feasibility Score */}
              {candidate.feasibility_score !== undefined && (
                <div className="mb-2">
                  <div className="flex justify-between mb-1">
                    <span className="text-xs text-slate-400">Feasibility</span>
                    <span className="text-xs text-slate-300">
                      {(candidate.feasibility_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${(candidate.feasibility_score / maxScore) * 100}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {/* Pros and Cons */}
              <div className="grid grid-cols-2 gap-3 mt-3 text-xs">
                {candidate.pros && candidate.pros.length > 0 && (
                  <div>
                    <p className="text-green-400 font-semibold mb-1">Pros</p>
                    <ul className="text-slate-400 space-y-1">
                      {candidate.pros.slice(0, 2).map((pro, i) => (
                        <li key={`pro-${i}`}>✓ {pro}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {candidate.cons && candidate.cons.length > 0 && (
                  <div>
                    <p className="text-red-400 font-semibold mb-1">Cons</p>
                    <ul className="text-slate-400 space-y-1">
                      {candidate.cons.slice(0, 2).map((con, i) => (
                        <li key={`con-${i}`}>✗ {con}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

CandidateComparison.propTypes = {
  candidates: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      rank: PropTypes.number.isRequired,
      option: PropTypes.string.isRequired,
      description: PropTypes.string,
      feasibility_score: PropTypes.number,
      pros: PropTypes.arrayOf(PropTypes.string),
      cons: PropTypes.arrayOf(PropTypes.string),
    })
  ),
};
