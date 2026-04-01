import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { getSharedWithMe, acceptShare, rejectShare, revokeShare } from '../utils/api';

function formatDate(dateStr, t) {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = Math.floor((now - date) / 1000);

  if (diff < 60) return t('postCard.justNow') || 'just now';
  if (diff < 3600) return t('postCard.timeAgo', { count: Math.floor(diff / 60) }) || `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return t('postCard.hoursAgo', { count: Math.floor(diff / 3600) }) || `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return t('postCard.daysAgo', { count: Math.floor(diff / 86400) }) || `${Math.floor(diff / 86400)}d ago`;

  return date.toLocaleDateString();
}

export default function SharedWithMeList() {
  const { t } = useTranslation();
  const [shares, setShares] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, pending, accepted

  useEffect(() => {
    loadShares();
  }, []);

  const loadShares = async () => {
    try {
      setLoading(true);
      const data = await getSharedWithMe(100);
      setShares(Array.isArray(data) ? data : data.shares || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (shareId) => {
    try {
      await acceptShare(shareId);
      loadShares();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleReject = async (shareId) => {
    if (!window.confirm(t('sharedWithMe.confirmReject') || 'Reject this share?')) {
      return;
    }

    try {
      await rejectShare(shareId);
      loadShares();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleRevoke = async (shareId) => {
    if (!window.confirm(t('sharedWithMe.confirmRevoke') || 'Stop sharing this post?')) {
      return;
    }

    try {
      await revokeShare(shareId);
      loadShares();
    } catch (err) {
      setError(err.message);
    }
  };

  const filteredShares = shares.filter(share => {
    if (filter === 'pending') return share.status === 'pending';
    if (filter === 'accepted') return share.status === 'accepted';
    return true;
  });

  if (loading) {
    return (
      <div className="p-6 text-center">
        <p className="text-slate-400 dark:text-slate-400">
          {t('common.loading') || 'Loading...'}
        </p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-100 dark:text-slate-100 mb-6">
        {t('sharedWithMe.title') || 'Posts Shared With Me'}
      </h1>

      {error && (
        <div className="mb-4 p-4 bg-red-900 text-red-100 rounded">
          {error}
        </div>
      )}

      {/* Filter buttons */}
      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded transition-colors ${
            filter === 'all'
              ? 'bg-blue-600 dark:bg-blue-600 text-white'
              : 'bg-slate-800 dark:bg-slate-800 text-slate-100 dark:text-slate-100 hover:bg-slate-700 dark:hover:bg-slate-700'
          }`}
        >
          {t('sharedWithMe.filterAll') || 'All'}
        </button>
        <button
          onClick={() => setFilter('pending')}
          className={`px-4 py-2 rounded transition-colors ${
            filter === 'pending'
              ? 'bg-blue-600 dark:bg-blue-600 text-white'
              : 'bg-slate-800 dark:bg-slate-800 text-slate-100 dark:text-slate-100 hover:bg-slate-700 dark:hover:bg-slate-700'
          }`}
        >
          {t('sharedWithMe.filterPending') || 'Pending'}
        </button>
        <button
          onClick={() => setFilter('accepted')}
          className={`px-4 py-2 rounded transition-colors ${
            filter === 'accepted'
              ? 'bg-blue-600 dark:bg-blue-600 text-white'
              : 'bg-slate-800 dark:bg-slate-800 text-slate-100 dark:text-slate-100 hover:bg-slate-700 dark:hover:bg-slate-700'
          }`}
        >
          {t('sharedWithMe.filterAccepted') || 'Accepted'}
        </button>
      </div>

      {/* Shares list */}
      {filteredShares.length === 0 ? (
        <div className="text-center p-6 bg-slate-800 dark:bg-slate-800 rounded border border-slate-700 dark:border-slate-700">
          <p className="text-slate-400 dark:text-slate-400">
            {t('sharedWithMe.noShares') || 'No shared posts yet'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredShares.map(share => (
            <div
              key={share.id}
              className="p-4 bg-slate-800 dark:bg-slate-800 rounded border border-slate-700 dark:border-slate-700 hover:border-blue-500 dark:hover:border-blue-500 transition-colors"
            >
              {/* Share header */}
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-bold text-slate-100 dark:text-slate-100">
                    {share.post_title || `Post ${share.post_id}`}
                  </h3>
                  <p className="text-sm text-slate-400 dark:text-slate-400">
                    {t('sharedWithMe.sharedBy') || 'Shared by'}: <span className="font-semibold">{share.owner_id}</span>
                  </p>
                  <p className="text-sm text-slate-400 dark:text-slate-400">
                    {formatDate(share.created_at, t)}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded text-sm font-semibold ${
                    share.status === 'pending'
                      ? 'bg-yellow-900 text-yellow-100'
                      : share.status === 'accepted'
                      ? 'bg-green-900 text-green-100'
                      : 'bg-red-900 text-red-100'
                  }`}
                >
                  {share.status}
                </span>
              </div>

              {/* Permission info */}
              <div className="mb-4 p-3 bg-slate-700 dark:bg-slate-700 rounded">
                <p className="text-sm text-slate-300 dark:text-slate-300">
                  {t('sharedWithMe.permission') || 'Permission'}: <span className="font-semibold">{share.permission}</span>
                </p>
                {share.expires_at && (
                  <p className="text-sm text-slate-400 dark:text-slate-400">
                    {t('sharedWithMe.expiresAt') || 'Expires at'}: {new Date(share.expires_at).toLocaleDateString()}
                  </p>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2 flex-wrap">
                {share.status === 'pending' ? (
                  <>
                    <button
                      onClick={() => handleAccept(share.id)}
                      className="px-4 py-2 bg-green-600 dark:bg-green-600 text-white rounded hover:bg-green-700 dark:hover:bg-green-700 transition-colors text-sm"
                    >
                      {t('sharedWithMe.accept') || 'Accept'}
                    </button>
                    <button
                      onClick={() => handleReject(share.id)}
                      className="px-4 py-2 bg-red-600 dark:bg-red-600 text-white rounded hover:bg-red-700 dark:hover:bg-red-700 transition-colors text-sm"
                    >
                      {t('sharedWithMe.reject') || 'Reject'}
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      to={`/post/${share.post_id}`}
                      className="px-4 py-2 bg-blue-600 dark:bg-blue-600 text-white rounded hover:bg-blue-700 dark:hover:bg-blue-700 transition-colors text-sm"
                    >
                      {t('sharedWithMe.view') || 'View'}
                    </Link>
                    <button
                      onClick={() => handleRevoke(share.id)}
                      className="px-4 py-2 bg-slate-700 dark:bg-slate-700 text-slate-100 dark:text-slate-100 rounded hover:bg-slate-600 dark:hover:bg-slate-600 transition-colors text-sm"
                    >
                      {t('sharedWithMe.stopSharing') || 'Stop Sharing'}
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
