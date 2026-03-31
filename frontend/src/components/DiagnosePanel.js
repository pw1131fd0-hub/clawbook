import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function DiagnosePanel({ result, onClose }) {
  if (!result) return null;

  const hasError = Boolean(result.error);

  return (
    <aside className="fixed right-0 top-0 h-full w-96 bg-slate-900 shadow-2xl border-l border-slate-700 flex flex-col z-50">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-700 bg-slate-800">
        <div>
          <h2 className="text-base font-semibold text-slate-100">🦞 Lobster Diagnosis Report</h2>
          {result.pod_name && (
            <p className="text-xs text-slate-400 mt-0.5 font-mono">{result.pod_name}</p>
          )}
        </div>
        <button
          onClick={onClose}
          className="text-slate-500 hover:text-slate-300 transition-colors"
          aria-label="Close panel"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-5">
        {hasError ? (
          <div className="rounded bg-red-900/30 border border-red-700 p-3 text-red-300 text-sm">
            ⚠️ {result.error}
          </div>
        ) : (
          <>
            {/* Error type badge */}
            {result.error_type && (
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-slate-400">Error Type:</span>
                <span className="px-2 py-0.5 rounded bg-red-900/40 text-red-300 text-xs font-mono border border-red-700">
                  {result.error_type}
                </span>
              </div>
            )}

            {/* Root cause */}
            <section>
              <h3 className="text-sm font-semibold text-slate-300 mb-1">🔍 Root Cause</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{result.root_cause}</p>
            </section>

            {/* Full analysis */}
            {result.raw_analysis && (
              <section>
                <h3 className="text-sm font-semibold text-slate-300 mb-1">📋 Analysis</h3>
                <div className="prose prose-sm max-w-none text-slate-400">
                  <ReactMarkdown>{result.raw_analysis}</ReactMarkdown>
                </div>
              </section>
            )}

            {/* Remediation */}
            {result.remediation && (
              <section>
                <h3 className="text-sm font-semibold text-slate-300 mb-1">🛠️ Remediation</h3>
                <div className="prose prose-sm max-w-none text-slate-400">
                  <ReactMarkdown>{result.remediation}</ReactMarkdown>
                </div>
              </section>
            )}

            {/* Model used */}
            {result.model_used && (
              <p className="text-xs text-slate-500 pt-2 border-t border-slate-700">
                Analyzed by: <span className="font-mono">{result.model_used}</span>
              </p>
            )}
          </>
        )}
      </div>
    </aside>
  );
}
