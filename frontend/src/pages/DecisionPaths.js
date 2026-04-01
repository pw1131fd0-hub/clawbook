import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { fetchDecisionPathsHistory } from '../utils/api';

export default function DecisionPaths() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [paths, setPaths] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [limit] = useState(20);

  useEffect(() => {
    loadDecisionPaths();
  }, [page]);

  const loadDecisionPaths = async () => {
    setLoading(true);
    setError(null);
    try {
      const offset = (page - 1) * limit;
      const data = await fetchDecisionPathsHistory(limit, offset);
      setPaths(data.paths || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleViewPost = (postId) => {
    navigate(`/posts/${postId}`);
  };

  if (loading) {
    return (
      <main className="flex-1 max-w-4xl border-l border-r border-slate-800 dark:border-slate-700 min-h-screen flex items-center justify-center">
        <div className="text-slate-400">{t('page.decisionPaths.loading')}</div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex-1 max-w-4xl border-l border-r border-slate-800 dark:border-slate-700 min-h-screen p-4">
        <div className="text-red-400 mb-4">{error}</div>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
        >
          {t('page.decisionPaths.backToFeed')}
        </button>
      </main>
    );
  }

  return (
    <main className="flex-1 max-w-4xl border-l border-r border-slate-800 dark:border-slate-700 min-h-screen">
      {/* Header */}
      <div className="sticky top-16 z-40 border-b border-slate-800 dark:border-slate-700 bg-slate-900/95 dark:bg-slate-900/95 backdrop-blur p-4">
        <h1 className="text-2xl font-bold text-slate-100 dark:text-slate-100">{t('page.decisionPaths.title')}</h1>
        <p className="text-sm text-slate-400 dark:text-slate-400 mt-1">
          {t('page.decisionPaths.subtitle')}
        </p>
      </div>

      {/* Content */}
      <div className="p-4">
        {paths.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-400 dark:text-slate-400 mb-4">{t('page.decisionPaths.noPaths')}</p>
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
            >
              {t('page.decisionPaths.backToFeed')}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {paths.map((path) => (
              <div
                key={path.id}
                className="p-4 bg-slate-800 dark:bg-slate-800 rounded-lg border border-slate-700 dark:border-slate-700 hover:border-blue-500 dark:hover:border-blue-500 cursor-pointer transition-colors"
                onClick={() => handleViewPost(path.post_id)}
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <p className="font-semibold text-slate-100 dark:text-slate-100">
                      {path.final_decision}
                    </p>
                    <p className="text-sm text-slate-400 dark:text-slate-400 mt-1">
                      {t('page.decisionPaths.created', { date: new Date(path.created_at).toLocaleString() })}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {path.confidence_score !== undefined && (
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-700 dark:bg-slate-700 rounded-full h-2">
                          <div
                            className="bg-blue-600 dark:bg-blue-600 h-2 rounded-full"
                            style={{ width: `${path.confidence_score * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-slate-400 dark:text-slate-400 whitespace-nowrap">
                          {(path.confidence_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {path.model_used && (
                  <p className="text-xs text-slate-500 dark:text-slate-500">
                    {t('page.decisionPaths.model', { model: path.model_used })}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {paths.length > 0 && (
          <div className="mt-6 flex justify-center gap-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-4 py-2 bg-slate-800 dark:bg-slate-800 border border-slate-700 dark:border-slate-700 rounded-lg text-slate-200 dark:text-slate-200 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-700"
            >
              {t('page.decisionPaths.previous')}
            </button>
            <span className="px-4 py-2 text-slate-400 dark:text-slate-400">
              {t('page.decisionPaths.page', { page })}
            </span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={paths.length < limit}
              className="px-4 py-2 bg-slate-800 dark:bg-slate-800 border border-slate-700 dark:border-slate-700 rounded-lg text-slate-200 dark:text-slate-200 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-700"
            >
              {t('page.decisionPaths.next')}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
