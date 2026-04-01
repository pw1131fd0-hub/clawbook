/**
 * NotificationBell Component
 * Displays real-time share notifications and activity notifications
 */

import React, { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useShareNotifications } from '../hooks/useWebSocket';

export default function NotificationBell({ userId, className = '' }) {
  const { t } = useTranslation();
  const [notifications, setNotifications] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  const handleShareNotification = useCallback((data) => {
    console.log('Share notification received:', data);

    // Show toast notification
    setToastMessage(data.message || `${data.sharer_id} shared a post with you`);
    setTimeout(() => setToastMessage(null), 5000);

    // Add to notification list
    const notification = {
      id: data.share_id,
      type: 'share',
      message: data.message,
      post_id: data.post_id,
      sharer_id: data.sharer_id,
      timestamp: data.timestamp,
      read: false,
    };

    setNotifications(prev => [notification, ...prev]);
  }, []);

  // Subscribe to share notifications
  useShareNotifications(handleShareNotification);

  const handleMarkAsRead = useCallback((notificationId) => {
    setNotifications(prev =>
      prev.map(n =>
        n.id === notificationId ? { ...n, read: true } : n
      )
    );
  }, []);

  const handleClearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <>
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-4 right-4 bg-green-600 dark:bg-green-600 text-white px-4 py-3 rounded-lg shadow-lg z-50 animate-pulse">
          <div className="flex items-center gap-2">
            <span>🔔</span>
            <span>{toastMessage}</span>
          </div>
        </div>
      )}

      {/* Notification Bell */}
      <div className={`relative ${className}`}>
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          className="relative p-2 text-slate-300 dark:text-slate-300 hover:text-slate-100 dark:hover:text-slate-100 transition-colors"
          title={t('notifications.bell') || 'Notifications'}
        >
          <span className="text-xl">🔔</span>
          {unreadCount > 0 && (
            <span className="absolute top-0 right-0 bg-red-600 dark:bg-red-600 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center">
              {unreadCount}
            </span>
          )}
        </button>

        {/* Dropdown Panel */}
        {showDropdown && (
          <div className="absolute right-0 top-full mt-2 w-80 bg-slate-800 dark:bg-slate-800 border border-slate-700 dark:border-slate-700 rounded-lg shadow-xl z-50">
            <div className="p-4 border-b border-slate-700 dark:border-slate-700 flex items-center justify-between">
              <h3 className="font-semibold text-slate-100 dark:text-slate-100">
                {t('notifications.title') || 'Notifications'}
              </h3>
              {notifications.length > 0 && (
                <button
                  onClick={handleClearNotifications}
                  className="text-xs text-slate-400 dark:text-slate-400 hover:text-slate-200 dark:hover:text-slate-200 transition-colors"
                >
                  {t('common.clear') || 'Clear All'}
                </button>
              )}
            </div>

            <div className="max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-4 text-center text-slate-400 dark:text-slate-400">
                  {t('notifications.empty') || 'No notifications'}
                </div>
              ) : (
                <div className="divide-y divide-slate-700 dark:divide-slate-700">
                  {notifications.map(notification => (
                    <div
                      key={notification.id}
                      onClick={() => handleMarkAsRead(notification.id)}
                      className={`p-4 cursor-pointer hover:bg-slate-750 dark:hover:bg-slate-750 transition-colors ${
                        notification.read ? '' : 'bg-slate-750 dark:bg-slate-750'
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        <span className="text-lg mt-1">
                          {notification.type === 'share' ? '📤' : '📢'}
                        </span>
                        <div className="flex-1">
                          <p className="text-sm text-slate-100 dark:text-slate-100">
                            {notification.message}
                          </p>
                          <p className="text-xs text-slate-400 dark:text-slate-400 mt-1">
                            {new Date(notification.timestamp).toLocaleString()}
                          </p>
                        </div>
                        {!notification.read && (
                          <span className="w-2 h-2 bg-blue-500 dark:bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Click outside to close */}
      {showDropdown && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowDropdown(false)}
        />
      )}
    </>
  );
}
