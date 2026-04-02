import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { api } from '../utils/api';

export default function WeeklySummary() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWeeklySummary = async () => {
      try {
        const response = await api.get('/weekly-summary/current');
        setSummary(response.data.data);
      } catch (err) {
        console.error('Error fetching weekly summary:', err);
        setError('Failed to load weekly summary');
      } finally {
        setLoading(false);
      }
    };

    fetchWeeklySummary();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 p-8 bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-700 rounded w-1/3"></div>
          <div className="h-64 bg-slate-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="flex-1 p-8 bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded">
          {error || 'Unable to load weekly summary'}
        </div>
      </div>
    );
  }

  const weekOverview = summary.week_overview || {};
  const achievements = summary.achievements || {};
  const habitPerformance = summary.habit_performance || {};
  const goalProgress = summary.goal_progress || {};
  const moodTrend = summary.mood_trend || {};
  const insights = summary.insights_summary || {};
  const nextWeekFocus = summary.next_week_focus || {};

  return (
    <div className="flex-1 p-8 bg-gradient-to-br from-slate-900 to-slate-800 min-h-screen">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-100 mb-2">📊 Weekly Summary</h1>
          <p className="text-slate-400">
            Week {weekOverview.week_number} • {new Date(weekOverview.week_start).toLocaleDateString()} - {new Date(weekOverview.week_end).toLocaleDateString()}
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <div className="text-3xl font-bold text-blue-400">{achievements.total_entries || 0}</div>
            <div className="text-slate-400 text-sm mt-2">Entries This Week</div>
          </div>
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <div className="text-3xl font-bold text-green-400">{habitPerformance.active_habits || 0}</div>
            <div className="text-slate-400 text-sm mt-2">Active Habits</div>
          </div>
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <div className="text-3xl font-bold text-amber-400">{goalProgress.active_goals || 0}</div>
            <div className="text-slate-400 text-sm mt-2">Active Goals</div>
          </div>
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <div className="text-3xl font-bold text-purple-400">{moodTrend.average_mood?.toFixed(1) || 5.0}</div>
            <div className="text-slate-400 text-sm mt-2">Average Mood</div>
          </div>
        </div>

        {/* Achievements */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-2xl font-bold text-slate-100 mb-4">✨ Top Achievements</h2>
          <div className="space-y-3">
            {(achievements.top_achievements || []).map((achievement, idx) => (
              <div key={idx} className="flex items-start space-x-4 p-4 bg-slate-700 rounded-lg hover:bg-slate-600 transition">
                <div className="text-2xl">{achievement.mood_emoji}</div>
                <div className="flex-1">
                  <div className="font-semibold text-slate-100">{achievement.title}</div>
                  <div className="text-sm text-slate-400 mt-1">{achievement.summary}</div>
                  <div className="text-xs text-slate-500 mt-2">
                    {new Date(achievement.date).toLocaleDateString()} • Mood: {achievement.mood}/10
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 text-center">
            <div className="inline-block bg-blue-900 text-blue-100 px-4 py-2 rounded text-sm">
              Consistency Score: {achievements.consistency_score || 0}%
            </div>
          </div>
        </div>

        {/* Habit Performance & Mood Trend */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Habit Performance */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h2 className="text-2xl font-bold text-slate-100 mb-4">📈 Habit Performance</h2>
            <div className="mb-4 text-center">
              <div className="text-3xl font-bold text-green-400">{Math.round(habitPerformance.performance_score || 0)}%</div>
              <div className="text-slate-400 text-sm">Overall Performance</div>
            </div>
            <div className="space-y-3">
              {(habitPerformance.habits || []).map((habit, idx) => (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-300 font-medium">{habit.name}</span>
                    <span className={`text-sm ${habit.completion_rate >= 70 ? 'text-green-400' : 'text-yellow-400'}`}>
                      {Math.round(habit.completion_rate)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${habit.completion_rate >= 70 ? 'bg-green-500' : 'bg-yellow-500'}`}
                      style={{ width: `${Math.min(habit.completion_rate, 100)}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-slate-500">Streak: {habit.streak || 0} days</div>
                </div>
              ))}
            </div>
          </div>

          {/* Mood Trend */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h2 className="text-2xl font-bold text-slate-100 mb-4">😊 Mood Trend</h2>
            <div className="mb-4 text-center space-y-2">
              <div className="text-3xl font-bold text-purple-400">{moodTrend.average_mood?.toFixed(1) || 5}/10</div>
              <div className={`text-sm font-medium capitalize ${
                moodTrend.mood_trend === 'improving' ? 'text-green-400' :
                moodTrend.mood_trend === 'declining' ? 'text-red-400' :
                'text-blue-400'
              }`}>
                {moodTrend.mood_trend || 'stable'} trend
              </div>
            </div>
            {moodTrend.moods && moodTrend.moods.length > 0 && (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={moodTrend.moods.map((mood, idx) => ({ day: `D${idx + 1}`, mood }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                  <XAxis dataKey="day" stroke="#94a3b8" />
                  <YAxis domain={[0, 10]} stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
                  <Line type="monotone" dataKey="mood" stroke="#a78bfa" dot={{ fill: '#a78bfa' }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Goal Progress */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-2xl font-bold text-slate-100 mb-4">🎯 Goal Progress</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-slate-700 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-400">{goalProgress.total_goals || 0}</div>
              <div className="text-sm text-slate-400">Total Goals</div>
            </div>
            <div className="bg-slate-700 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-amber-400">{goalProgress.active_goals || 0}</div>
              <div className="text-sm text-slate-400">Active Goals</div>
            </div>
            <div className="bg-slate-700 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-400">{goalProgress.completed_goals || 0}</div>
              <div className="text-sm text-slate-400">Completed</div>
            </div>
          </div>
          <div className="space-y-3">
            {(goalProgress.progress_items || []).map((goal, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-slate-300 font-medium">{goal.name}</span>
                  <span className="text-sm text-slate-500">{goal.progress}/{goal.target}</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-blue-500 transition-all"
                    style={{ width: `${Math.min((goal.progress / goal.target) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Insights */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-2xl font-bold text-slate-100 mb-4">💡 Key Insights</h2>
          <div className="space-y-3">
            {(insights.insights || []).map((insight, idx) => (
              <div key={idx} className="flex items-start space-x-4 p-4 bg-slate-700 rounded-lg">
                <div className="text-2xl">{insight.emoji}</div>
                <div className="flex-1">
                  <div className="text-slate-100">{insight.text}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Next Week Focus */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mb-12">
          <h2 className="text-2xl font-bold text-slate-100 mb-4">🎯 Next Week Focus</h2>
          <div className="space-y-3">
            {(nextWeekFocus.focus_areas || []).map((area, idx) => (
              <div key={idx} className={`flex items-start space-x-4 p-4 rounded-lg border-l-4 ${
                area.priority === 'high' ? 'bg-red-900/30 border-red-500' :
                area.priority === 'medium' ? 'bg-yellow-900/30 border-yellow-500' :
                'bg-green-900/30 border-green-500'
              }`}>
                <div className="text-2xl">{area.emoji}</div>
                <div className="flex-1">
                  <div className="text-slate-100 font-medium">{area.text}</div>
                  <div className="text-sm text-slate-400 mt-1 capitalize">{area.category} • Priority: {area.priority}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
