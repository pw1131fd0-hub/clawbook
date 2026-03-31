import React, { useState } from 'react';
import { diagnosePod } from '../utils/api';

const STATUS_CONFIG = {
  Running: { color: 'bg-green-500', text: 'text-green-300', label: 'Running' },
  Pending: { color: 'bg-yellow-400', text: 'text-yellow-300', label: 'Pending' },
  Failed: { color: 'bg-red-500', text: 'text-red-300', label: 'Failed' },
  Succeeded: { color: 'bg-blue-400', text: 'text-blue-300', label: 'Succeeded' },
  Unknown: { color: 'bg-slate-500', text: 'text-slate-300', label: 'Unknown' },
};

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.Unknown;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${cfg.text} bg-opacity-10`}>
      <span className={`w-2 h-2 rounded-full ${cfg.color}`} />
      {cfg.label}
    </span>
  );
}

export default function PodList({ pods, loading, error, onDiagnoseResult }) {
  const [diagnosing, setDiagnosing] = useState({});

  const handleDiagnose = async (pod) => {
    setDiagnosing((prev) => ({ ...prev, [pod.name]: true }));
    try {
      const result = await diagnosePod(pod.name, pod.namespace);
      onDiagnoseResult && onDiagnoseResult(result);
    } catch (e) {
      onDiagnoseResult && onDiagnoseResult({ error: e.message, pod_name: pod.name });
    } finally {
      setDiagnosing((prev) => ({ ...prev, [pod.name]: false }));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-400">
        <svg className="animate-spin h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
        </svg>
        Loading pods...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-900/30 border border-red-700 p-4 text-red-300 text-sm">
        ⚠️ {error}
      </div>
    );
  }

  const unhealthy = pods.filter((p) => p.status !== 'Running' && p.status !== 'Succeeded');
  const healthy = pods.filter((p) => p.status === 'Running' || p.status === 'Succeeded');

  return (
    <div className="space-y-4">
      {unhealthy.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-red-400 mb-2">
            ⚠️ Unhealthy Pods ({unhealthy.length})
          </h3>
          <PodTable pods={unhealthy} diagnosing={diagnosing} onDiagnose={handleDiagnose} highlight />
        </section>
      )}
      <section>
        <h3 className="text-sm font-semibold text-slate-400 mb-2">
          All Pods ({pods.length})
        </h3>
        <PodTable pods={pods} diagnosing={diagnosing} onDiagnose={handleDiagnose} />
      </section>
    </div>
  );
}

function PodTable({ pods, diagnosing, onDiagnose, highlight }) {
  if (pods.length === 0) return <p className="text-sm text-slate-400">No pods to display.</p>;

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-700">
      <table className="min-w-full divide-y divide-slate-700 text-sm">
        <thead className="bg-slate-800">
          <tr>
            {['Name', 'Namespace', 'Status', 'IP', 'Actions'].map((h) => (
              <th key={h} className="px-4 py-2 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-slate-800 divide-y divide-slate-700">
          {pods.map((pod) => (
            <tr key={`${pod.namespace}/${pod.name}`} className={highlight && pod.status !== 'Running' ? 'bg-red-900/20' : ''}>
              <td className="px-4 py-2 font-mono text-xs text-slate-100">{pod.name}</td>
              <td className="px-4 py-2 text-slate-400">{pod.namespace}</td>
              <td className="px-4 py-2"><StatusBadge status={pod.status} /></td>
              <td className="px-4 py-2 font-mono text-xs text-slate-500">{pod.ip || '—'}</td>
              <td className="px-4 py-2">
                <button
                  onClick={() => onDiagnose(pod)}
                  disabled={diagnosing[pod.name]}
                  className="px-3 py-1 text-xs font-medium rounded bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-wait transition-colors"
                >
                  {diagnosing[pod.name] ? 'Diagnosing…' : 'Diagnose'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
