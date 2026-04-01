import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { sharePost, getGroups } from '../utils/api';

export default function ShareModal({ postId, onClose, onShared }) {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [userEmails, setUserEmails] = useState('');
  const [groups, setGroups] = useState([]);
  const [selectedGroups, setSelectedGroups] = useState([]);
  const [permission, setPermission] = useState('read');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      const groupsData = await getGroups();
      setGroups(groupsData);
    } catch (err) {
      console.error('Failed to load groups:', err);
    }
  };

  const handleShare = async () => {
    if (!userEmails.trim() && selectedGroups.length === 0) {
      setError(t('shareModal.selectRecipients') || 'Select users or groups');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const emails = userEmails
        .split(',')
        .map(e => e.trim())
        .filter(e => e.length > 0);

      await sharePost(postId, emails, selectedGroups, permission);
      setSuccess(true);
      setTimeout(() => {
        onShared?.();
        onClose();
      }, 1000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleGroup = (groupId) => {
    if (selectedGroups.includes(groupId)) {
      setSelectedGroups(selectedGroups.filter(g => g !== groupId));
    } else {
      setSelectedGroups([...selectedGroups, groupId]);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-slate-800 dark:bg-slate-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h2 className="text-xl font-bold text-slate-100 dark:text-slate-100 mb-4">
          {t('shareModal.title') || 'Share Post'}
        </h2>

        {error && (
          <div className="mb-4 p-3 bg-red-900 text-red-100 rounded">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 p-3 bg-green-900 text-green-100 rounded">
            {t('shareModal.success') || 'Post shared successfully!'}
          </div>
        )}

        {/* User emails input */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-300 dark:text-slate-300 mb-2">
            {t('shareModal.emailsLabel') || 'User emails (comma separated)'}
          </label>
          <textarea
            value={userEmails}
            onChange={(e) => setUserEmails(e.target.value)}
            placeholder="user1@example.com, user2@example.com"
            className="w-full px-3 py-2 bg-slate-700 dark:bg-slate-700 text-slate-100 dark:text-slate-100 rounded border border-slate-600 dark:border-slate-600 focus:outline-none focus:border-blue-500 dark:focus:border-blue-500 resize-none h-20"
          />
        </div>

        {/* Groups selection */}
        {groups.length > 0 && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-300 dark:text-slate-300 mb-2">
              {t('shareModal.groupsLabel') || 'Collaboration Groups'}
            </label>
            <div className="space-y-2">
              {groups.map(group => (
                <label key={group.id} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedGroups.includes(group.id)}
                    onChange={() => toggleGroup(group.id)}
                    className="rounded"
                  />
                  <span className="text-slate-100 dark:text-slate-100">{group.name}</span>
                  <span className="text-xs text-slate-400 dark:text-slate-400">
                    ({group.member_count} members)
                  </span>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Permission selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-300 dark:text-slate-300 mb-2">
            {t('shareModal.permissionLabel') || 'Permission Level'}
          </label>
          <select
            value={permission}
            onChange={(e) => setPermission(e.target.value)}
            className="w-full px-3 py-2 bg-slate-700 dark:bg-slate-700 text-slate-100 dark:text-slate-100 rounded border border-slate-600 dark:border-slate-600 focus:outline-none focus:border-blue-500 dark:focus:border-blue-500"
          >
            <option value="read">{t('shareModal.readOnly') || 'Read Only'}</option>
            <option value="comment">{t('shareModal.canComment') || 'Can Comment'}</option>
            <option value="edit">{t('shareModal.canEdit') || 'Can Edit'}</option>
          </select>
        </div>

        {/* Action buttons */}
        <div className="flex gap-2">
          <button
            onClick={onClose}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-slate-700 dark:bg-slate-700 text-slate-100 dark:text-slate-100 rounded hover:bg-slate-600 dark:hover:bg-slate-600 disabled:opacity-50 transition-colors"
          >
            {t('common.cancel') || 'Cancel'}
          </button>
          <button
            onClick={handleShare}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-blue-600 dark:bg-blue-600 text-white rounded hover:bg-blue-700 dark:hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {loading ? (t('common.loading') || 'Sharing...') : (t('shareModal.share') || 'Share')}
          </button>
        </div>
      </div>
    </div>
  );
}
