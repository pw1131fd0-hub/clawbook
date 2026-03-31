import React, { useState, useEffect } from 'react';
import { API_URL } from '../utils/api';

export default function SlackConfigModal({ isOpen, onClose, onSuccess }) {
  const [webhookUrl, setWebhookUrl] = useState('');
  const [enabled, setEnabled] = useState(true);
  const [summaryEnabled, setSummaryEnabled] = useState(true);
  const [summaryTime, setSummaryTime] = useState('09:00');
  const [highMoodEnabled, setHighMoodEnabled] = useState(true);
  const [highMoodThreshold, setHighMoodThreshold] = useState(4);
  const [milestoneEnabled, setMilestoneEnabled] = useState(true);
  const [includeFullContent, setIncludeFullContent] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [hasConfig, setHasConfig] = useState(false);

  // Load existing config on mount
  useEffect(() => {
    if (isOpen) {
      loadConfig();
    }
  }, [isOpen]);

  const loadConfig = async () => {
    try {
      const response = await fetch(`${API_URL}/slack/config`);
      if (response.ok) {
        const data = await response.json();
        if (data) {
          setWebhookUrl(data.webhook_url || '');
          setEnabled(data.enabled ?? true);
          setSummaryEnabled(data.summary_enabled ?? true);
          setSummaryTime(data.summary_time || '09:00');
          setHighMoodEnabled(data.high_mood_enabled ?? true);
          setHighMoodThreshold(data.high_mood_threshold ?? 4);
          setMilestoneEnabled(data.milestone_enabled ?? true);
          setIncludeFullContent(data.include_full_content ?? false);
          setHasConfig(true);
        }
      }
    } catch (err) {
      // No config exists yet, that's okay
      setHasConfig(false);
    }
  };

  const handleTestWebhook = async (e) => {
    e.preventDefault();
    setIsTesting(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${API_URL}/slack/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Webhook test failed');
      }

      setSuccess('Webhook test successful! ✅');
    } catch (err) {
      setError(err.message || 'Test failed. Please check the webhook URL.');
    } finally {
      setIsTesting(false);
    }
  };

  const handleSaveConfig = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      // Validate webhook URL
      if (!webhookUrl.trim()) {
        throw new Error('Webhook URL is required');
      }

      const configData = {
        webhook_url: webhookUrl,
        enabled,
        summary_enabled: summaryEnabled,
        summary_time: summaryTime,
        high_mood_enabled: highMoodEnabled,
        high_mood_threshold: highMoodThreshold,
        milestone_enabled: milestoneEnabled,
        include_full_content: includeFullContent,
      };

      const method = hasConfig ? 'PUT' : 'POST';
      const response = await fetch(`${API_URL}/slack/config`, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(configData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save configuration');
      }

      setSuccess('Slack configuration saved successfully! 🎉');
      setHasConfig(true);
      if (onSuccess) onSuccess();
    } catch (err) {
      setError(err.message || 'Failed to save configuration. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteConfig = async () => {
    if (!window.confirm('Are you sure you want to delete the Slack configuration?')) {
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${API_URL}/slack/config`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete configuration');
      }

      setSuccess('Slack configuration deleted successfully.');
      setWebhookUrl('');
      setEnabled(true);
      setHasConfig(false);
      setTimeout(() => onClose(), 1500);
    } catch (err) {
      setError(err.message || 'Failed to delete configuration. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-slate-900 rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4 dark:bg-slate-800 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4 text-slate-100">🌐 Slack Integration</h2>

        <form onSubmit={handleSaveConfig} className="space-y-4">
          {/* Webhook URL */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Slack Webhook URL *
            </label>
            <input
              type="url"
              value={webhookUrl}
              onChange={(e) => setWebhookUrl(e.target.value)}
              placeholder="https://hooks.slack.com/services/..."
              className="w-full px-4 py-2 rounded-lg bg-slate-800 text-slate-100 border border-slate-700 focus:outline-none focus:border-blue-500 font-mono text-sm"
            />
            <p className="text-xs text-slate-400 mt-1">Get your webhook URL from Slack's incoming webhooks</p>
          </div>

          {/* Enable / Disable */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="enabled"
              checked={enabled}
              onChange={(e) => setEnabled(e.target.checked)}
              className="w-4 h-4 rounded bg-slate-700 border border-slate-600 cursor-pointer"
            />
            <label htmlFor="enabled" className="ml-3 text-sm font-medium text-slate-300 cursor-pointer">
              Enable Slack notifications
            </label>
          </div>

          <div className="border-t border-slate-700 pt-4">
            <h3 className="text-lg font-semibold text-slate-200 mb-4">📬 Notification Rules</h3>

            {/* Daily Summary */}
            <div className="mb-4 p-4 bg-slate-800 rounded-lg">
              <div className="flex items-center mb-3">
                <input
                  type="checkbox"
                  id="summaryEnabled"
                  checked={summaryEnabled}
                  onChange={(e) => setSummaryEnabled(e.target.checked)}
                  className="w-4 h-4 rounded bg-slate-700 border border-slate-600 cursor-pointer"
                />
                <label htmlFor="summaryEnabled" className="ml-3 text-sm font-medium text-slate-300 cursor-pointer">
                  📅 Daily Summary Notification
                </label>
              </div>
              {summaryEnabled && (
                <div className="ml-7">
                  <label className="block text-xs text-slate-400 mb-2">Send daily summary at:</label>
                  <input
                    type="time"
                    value={summaryTime}
                    onChange={(e) => setSummaryTime(e.target.value)}
                    className="px-3 py-1 rounded bg-slate-700 text-slate-100 border border-slate-600 focus:outline-none focus:border-blue-500 text-sm"
                  />
                </div>
              )}
            </div>

            {/* High Mood Posts */}
            <div className="mb-4 p-4 bg-slate-800 rounded-lg">
              <div className="flex items-center mb-3">
                <input
                  type="checkbox"
                  id="highMoodEnabled"
                  checked={highMoodEnabled}
                  onChange={(e) => setHighMoodEnabled(e.target.checked)}
                  className="w-4 h-4 rounded bg-slate-700 border border-slate-600 cursor-pointer"
                />
                <label htmlFor="highMoodEnabled" className="ml-3 text-sm font-medium text-slate-300 cursor-pointer">
                  ⭐ High Mood Notifications
                </label>
              </div>
              {highMoodEnabled && (
                <div className="ml-7">
                  <label className="block text-xs text-slate-400 mb-2">Send notification when mood score exceeds:</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    step="0.5"
                    value={highMoodThreshold}
                    onChange={(e) => setHighMoodThreshold(parseFloat(e.target.value))}
                    className="px-3 py-1 rounded bg-slate-700 text-slate-100 border border-slate-600 focus:outline-none focus:border-blue-500 text-sm w-20"
                  />
                </div>
              )}
            </div>

            {/* Milestones */}
            <div className="mb-4 p-4 bg-slate-800 rounded-lg">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="milestoneEnabled"
                  checked={milestoneEnabled}
                  onChange={(e) => setMilestoneEnabled(e.target.checked)}
                  className="w-4 h-4 rounded bg-slate-700 border border-slate-600 cursor-pointer"
                />
                <label htmlFor="milestoneEnabled" className="ml-3 text-sm font-medium text-slate-300 cursor-pointer">
                  🎯 Milestone Notifications
                </label>
              </div>
              <p className="text-xs text-slate-400 ml-7 mt-1">Notify on consecutive days, mood improvements, etc.</p>
            </div>

            {/* Content Privacy */}
            <div className="mb-4 p-4 bg-slate-800 rounded-lg">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="includeFullContent"
                  checked={includeFullContent}
                  onChange={(e) => setIncludeFullContent(e.target.checked)}
                  className="w-4 h-4 rounded bg-slate-700 border border-slate-600 cursor-pointer"
                />
                <label htmlFor="includeFullContent" className="ml-3 text-sm font-medium text-slate-300 cursor-pointer">
                  📝 Include full post content in notifications
                </label>
              </div>
              <p className="text-xs text-slate-400 ml-7 mt-1">
                {includeFullContent ? 'Full posts will be sent to Slack' : 'Only summaries will be sent to Slack'}
              </p>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-900 text-red-100 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="p-3 bg-green-900 text-green-100 rounded-lg text-sm">
              {success}
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3 pt-4 border-t border-slate-700">
            {hasConfig && (
              <button
                type="button"
                onClick={handleDeleteConfig}
                disabled={isLoading}
                className="px-4 py-2 rounded-lg bg-red-900 text-red-100 font-medium hover:bg-red-800 disabled:bg-red-400 transition-colors text-sm"
              >
                Delete Configuration
              </button>
            )}
            <div className="flex-1"></div>
            <button
              type="button"
              onClick={handleTestWebhook}
              disabled={isLoading || isTesting || !webhookUrl}
              className="px-4 py-2 rounded-lg bg-slate-700 text-slate-100 font-medium hover:bg-slate-600 disabled:bg-slate-500 transition-colors"
            >
              {isTesting ? 'Testing...' : 'Test Webhook'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-slate-700 text-slate-100 font-medium hover:bg-slate-600 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:bg-blue-400 transition-colors"
            >
              {isLoading ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
