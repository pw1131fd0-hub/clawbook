import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { api } from '../utils/api';

export default function Analytics() {
  const { t } = useTranslation();
  const [days, setDays] = useState(30);
  const [granularity, setGranularity] = useState('daily');
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalyticsData();
  }, [days, granularity]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/analytics/sentiment', {
        params: {
          days,
          granularity,
        },
      });
      setAnalyticsData(response.data);
    } catch (err) {
      setError('Failed to load analytics data');
      console.error('Analytics error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderTrendChart = () => {
    if (!analyticsData?.trends || analyticsData.trends.length === 0) {
      return null;
    }

    return (
      <div className="bg-slate-800 dark:bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold text-slate-100 mb-4">
          📈 Sentiment Trend
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={analyticsData.trends}>
            <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
            <XAxis dataKey="date" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" domain={[0, 10]} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
              labelStyle={{ color: '#f1f5f9' }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="sentiment"
              stroke="#E85D4C"
              strokeWidth={2}
              dot={{ fill: '#E85D4C' }}
              name="Sentiment Score"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderMoodDistribution = () => {
    if (!analyticsData?.mood_distribution) {
      return null;
    }

    const moodData = Object.entries(analyticsData.mood_distribution).map(([mood, count]) => ({
      mood,
      count,
    }));

    return (
      <div className="bg-slate-800 dark:bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold text-slate-100 mb-4">
          😊 Mood Distribution
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={moodData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
            <XAxis dataKey="mood" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
              labelStyle={{ color: '#f1f5f9' }}
            />
            <Legend />
            <Bar
              dataKey="count"
              fill="#3B82F6"
              name="Post Count"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderStats = () => {
    if (!analyticsData) {
      return null;
    }

    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-800 dark:bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="text-xs text-slate-400 mb-1">Total Posts</div>
          <div className="text-2xl font-bold text-slate-100">
            {analyticsData.total_posts}
          </div>
        </div>

        <div className="bg-slate-800 dark:bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="text-xs text-slate-400 mb-1">Avg Sentiment</div>
          <div className="text-2xl font-bold text-slate-100">
            {analyticsData.average_sentiment.toFixed(1)}/10
          </div>
        </div>

        <div className="bg-slate-800 dark:bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="text-xs text-slate-400 mb-1">Best Day</div>
          <div className="text-2xl font-bold text-green-400">
            {analyticsData.max_sentiment.toFixed(1)}
          </div>
        </div>

        <div className="bg-slate-800 dark:bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="text-xs text-slate-400 mb-1">Toughest Day</div>
          <div className="text-2xl font-bold text-red-400">
            {analyticsData.min_sentiment.toFixed(1)}
          </div>
        </div>
      </div>
    );
  };

  const renderInsights = () => {
    if (!analyticsData?.insights || analyticsData.insights.length === 0) {
      return null;
    }

    return (
      <div className="bg-slate-800 dark:bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold text-slate-100 mb-4">
          💡 Insights
        </h3>
        <ul className="space-y-2">
          {analyticsData.insights.map((insight, idx) => (
            <li key={idx} className="text-slate-300 flex items-start">
              <span className="text-slate-400 mr-2">•</span>
              <span>{insight}</span>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <main className="flex-1 max-w-6xl mx-auto min-h-screen">
      {/* Header */}
      <div className="sticky top-16 z-30 border-b border-slate-800 dark:border-slate-700 bg-slate-900/95 dark:bg-slate-900/95 backdrop-blur px-6 py-4">
        <h1 className="text-2xl font-bold text-slate-100 dark:text-slate-100">
          📊 {t('page.analytics.title', 'Sentiment Analytics')}
        </h1>
        <p className="text-sm text-slate-400 dark:text-slate-400 mt-1">
          {t('page.analytics.subtitle', 'Visualize your emotional patterns and growth over time')}
        </p>
      </div>

      {/* Controls */}
      <div className="px-6 py-4 border-b border-slate-800 dark:border-slate-700 bg-slate-800/50">
        <div className="flex gap-4 flex-wrap">
          <div className="flex gap-2">
            <label className="text-sm text-slate-400 self-center">Period:</label>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="px-3 py-1 rounded bg-slate-700 text-slate-100 text-sm border border-slate-600 focus:border-blue-500 focus:outline-none"
            >
              <option value={30}>30 days</option>
              <option value={60}>60 days</option>
              <option value={90}>90 days</option>
            </select>
          </div>

          <div className="flex gap-2">
            <label className="text-sm text-slate-400 self-center">Granularity:</label>
            <select
              value={granularity}
              onChange={(e) => setGranularity(e.target.value)}
              className="px-3 py-1 rounded bg-slate-700 text-slate-100 text-sm border border-slate-600 focus:border-blue-500 focus:outline-none"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {error && (
          <div className="p-4 bg-red-900/20 border border-red-800 rounded text-red-300">
            {error}
          </div>
        )}

        {loading ? (
          <div className="p-6 bg-slate-800 dark:bg-slate-800 rounded-lg text-center text-slate-400">
            Loading analytics...
          </div>
        ) : analyticsData ? (
          <>
            {renderStats()}
            {renderTrendChart()}
            {renderMoodDistribution()}
            {renderInsights()}
          </>
        ) : (
          <div className="p-6 bg-slate-800 dark:bg-slate-800 rounded-lg text-center text-slate-400">
            No data available. Start journaling to see your analytics!
          </div>
        )}
      </div>
    </main>
  );
}
