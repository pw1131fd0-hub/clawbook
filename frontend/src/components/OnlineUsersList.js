/**
 * OnlineUsersList Component
 * Displays real-time list of online users in a collaboration group
 */

import React, { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useGroupPresence } from '../hooks/useWebSocket';

export default function OnlineUsersList({ groupId, className = '' }) {
  const { t } = useTranslation();
  const [onlineUsers, setOnlineUsers] = useState([]);

  const handleUserOnline = useCallback((data) => {
    console.log('User online:', data);
    if (data.online_users) {
      setOnlineUsers(data.online_users);
    } else if (data.user_id) {
      setOnlineUsers(prev => {
        if (!prev.includes(data.user_id)) {
          return [...prev, data.user_id];
        }
        return prev;
      });
    }
  }, []);

  const handleUserOffline = useCallback((data) => {
    console.log('User offline:', data);
    if (data.remaining_users) {
      setOnlineUsers(data.remaining_users);
    } else if (data.user_id) {
      setOnlineUsers(prev => prev.filter(u => u !== data.user_id));
    }
  }, []);

  // Subscribe to presence updates
  useGroupPresence(groupId, handleUserOnline, handleUserOffline);

  if (!groupId) {
    return null;
  }

  return (
    <div className={`bg-slate-750 dark:bg-slate-750 border border-slate-700 dark:border-slate-700 rounded-lg p-3 ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-semibold text-slate-100 dark:text-slate-100">
          {t('onlineUsers.title') || 'Online Members'}
        </h4>
        <span className="bg-slate-700 dark:bg-slate-700 text-slate-300 dark:text-slate-300 text-xs px-2 py-1 rounded">
          {onlineUsers.length} {onlineUsers.length === 1 ? t('onlineUsers.member') || 'member' : t('onlineUsers.members') || 'members'}
        </span>
      </div>

      <div className="space-y-1">
        {onlineUsers.length === 0 ? (
          <div className="text-xs text-slate-400 dark:text-slate-400 italic">
            {t('onlineUsers.noUsers') || 'No users online'}
          </div>
        ) : (
          onlineUsers.map(userId => (
            <div
              key={userId}
              className="flex items-center gap-2 p-2 bg-slate-700 dark:bg-slate-700 rounded hover:bg-slate-650 dark:hover:bg-slate-650 transition-colors"
            >
              <span className="inline-flex items-center justify-center w-6 h-6 bg-green-600 dark:bg-green-600 text-white text-xs rounded-full font-semibold">
                {userId.charAt(0).toUpperCase()}
              </span>
              <span className="text-sm text-slate-200 dark:text-slate-200 truncate">
                {userId}
              </span>
              <span className="ml-auto flex items-center gap-1">
                <span className="inline-block w-2 h-2 bg-green-500 dark:bg-green-500 rounded-full animate-pulse" />
                <span className="text-xs text-green-400 dark:text-green-400">
                  {t('onlineUsers.online') || 'Online'}
                </span>
              </span>
            </div>
          ))
        )}
      </div>

      {onlineUsers.length > 0 && (
        <div className="mt-3 pt-3 border-t border-slate-600 dark:border-slate-600 text-xs text-slate-400 dark:text-slate-400">
          {t('onlineUsers.realTime') || 'Real-time updates enabled'}
        </div>
      )}
    </div>
  );
}
