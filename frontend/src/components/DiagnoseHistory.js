import React, { useState, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import { fetchDiagnoseHistory, fetchPodDiagnoseHistory } from '../utils/api';

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function parseAnalysis(aiAnalysis) {
  if (!aiAnalysis) return null;
  try {
    return JSON.parse(aiAnalysis);
  } catch {
    return { raw: aiAnalysis };
  }
}

function HistoryCard({ record, onSelect, isSelected }) {
  const errorTypeClass = record.error_type && record.error_type !== 'Unknown'
    ? 'bg-red-900/40 text-red-300 border border-red-700'
    : 'bg-slate-700 text-slate-300';

  return (
    <div
      onClick={() => onSelect(record)}
      className={`cursor-pointer rounded-xl border p-4 transition-all hover:shadow-md ${
        isSelected ? 'border-indigo-500 ring-2 ring-indigo-500/30 bg-slate-800' : 'border-slate-700 bg-slate-800'
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="font-mono text-sm font-medium text-slate-100 truncate">{record.pod_name}</p>
          <p className="text-xs text-slate-400 mt-0.5">{record.namespace}</p>
        </div>
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full shrink-0 ${errorTypeClass}`}>
          {record.error_type || 'N/A'}
        </span>
      </div>
      <p className="text-xs text-slate-500 mt-2">{formatDate(record.created_at)}</p>
    </div>
  );
}

function DetailPanel({ record, onClose }) {
  const analysis = parseAnalysis(record.ai_analysis);

  return (
    <aside className="fixed right-0 top-0 h-full w-[28rem] bg-slate-900 shadow-2xl border-l border-slate-700 flex flex-col z-50">
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-700 bg-slate-800">
        <div>
          <h2 className="text-base font-semibold text-slate-100">📜 Diagnosis Record</h2>
          <p className="text-xs text-slate-400 mt-0.5 font-mono truncate max-w-[280px]">{record.pod_name}</p>
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

      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-5">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-xs text-slate-400 uppercase tracking-wide">Namespace</span>
            <p className="font-medium text-slate-100">{record.namespace}</p>
          </div>
          <div>
            <span className="text-xs text-slate-400 uppercase tracking-wide">Error Type</span>
            <p className="font-mono text-sm text-red-300">{record.error_type || 'Unknown'}</p>
          </div>
          <div className="col-span-2">
            <span className="text-xs text-slate-400 uppercase tracking-wide">Diagnosed At</span>
            <p className="text-slate-300">{new Date(record.created_at).toLocaleString()}</p>
          </div>
        </div>

        {analysis && (
          <>
            {analysis.root_cause && (
              <section>
                <h3 className="text-sm font-semibold text-slate-300 mb-1">🔍 Root Cause</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{analysis.root_cause}</p>
              </section>
            )}
            {analysis.detailed_analysis && (
              <section>
                <h3 className="text-sm font-semibold text-slate-300 mb-1">📋 Detailed Analysis</h3>
                <div className="prose prose-sm max-w-none text-slate-400">
                  <ReactMarkdown>{analysis.detailed_analysis}</ReactMarkdown>
                </div>
              </section>
            )}
            {analysis.remediation && (
              <section>
                <h3 className="text-sm font-semibold text-slate-300 mb-1">🛠️ Remediation</h3>
                <div className="prose prose-sm max-w-none text-slate-400">
                  <ReactMarkdown>{analysis.remediation}</ReactMarkdown>
                </div>
              </section>
            )}
            {analysis.raw && (
              <section>
                <h3 className="text-sm font-semibold text-slate-300 mb-1">📄 Raw Output</h3>
                <pre className="text-xs bg-slate-800 border border-slate-700 rounded p-3 overflow-auto max-h-64 whitespace-pre-wrap text-slate-400">
                  {analysis.raw}
                </pre>
              </section>
            )}
          </>
        )}

        {!analysis && (
          <p className="text-sm text-slate-500 italic">No analysis data available.</p>
        )}
      </div>
    </aside>
  );
}

export default function DiagnoseHistory() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null);
  const [searchPod, setSearchPod] = useState('');
  const [searchMode, setSearchMode] = useState('all');

  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      let data;
      if (searchMode === 'pod' && searchPod.trim()) {
        data = await fetchPodDiagnoseHistory(searchPod.trim());
      } else {
        data = await fetchDiagnoseHistory(100);
      }
      setRecords(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e.message || 'Failed to load history');
    } finally {
      setLoading(false);
    }
  }, [searchMode, searchPod]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleSearch = (e) => {
    e.preventDefault();
    loadHistory();
  };

  const filteredRecords = records.filter((r) => {
    if (!searchPod.trim()) return true;
    if (searchMode === 'pod') return true;
    return r.pod_name.toLowerCase().includes(searchPod.toLowerCase());
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-gray-700">📜 Diagnose History</h2>
        <button
          onClick={loadHistory}
          disabled={loading}
          className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-indigo-600 px-3 py-1.5 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-all disabled:opacity-40"
        >
          <svg className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      <form onSubmit={handleSearch} className="flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-2">
          <select
            value={searchMode}
            onChange={(e) => setSearchMode(e.target.value)}
            className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white focus:outline-none focus:border-indigo-400"
          >
            <option value="all">All Records</option>
            <option value="filter">Filter by Name</option>
            <option value="pod">Exact Pod Match</option>
          </select>
          {searchMode !== 'all' && (
            <input
              type="text"
              value={searchPod}
              onChange={(e) => setSearchPod(e.target.value)}
              placeholder="Pod name..."
              className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 w-52 focus:outline-none focus:border-indigo-400"
            />
          )}
          {searchMode === 'pod' && (
            <button
              type="submit"
              className="px-3 py-1.5 text-sm font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
            >
              Search
            </button>
          )}
        </div>
        <span className="text-xs text-gray-400 ml-auto">
          {filteredRecords.length} record{filteredRecords.length !== 1 ? 's' : ''}
        </span>
      </form>

      {loading && (
        <div className="flex items-center justify-center h-40 text-gray-400">
          <svg className="animate-spin h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
          </svg>
          Loading history...
        </div>
      )}

      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-red-700 text-sm">
          ⚠️ {error}
        </div>
      )}

      {!loading && !error && filteredRecords.length === 0 && (
        <div className="rounded-xl bg-gray-50 border border-gray-200 p-8 text-center text-gray-500">
          <p className="text-lg mb-1">🦞</p>
          <p className="text-sm">No diagnosis records found.</p>
          <p className="text-xs text-gray-400 mt-1">Diagnose a pod to see history here.</p>
        </div>
      )}

      {!loading && !error && filteredRecords.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {filteredRecords.map((r) => (
            <HistoryCard
              key={r.id}
              record={r}
              onSelect={setSelected}
              isSelected={selected?.id === r.id}
            />
          ))}
        </div>
      )}

      {selected && <DetailPanel record={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
