import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { LineChart, Line, BarChart, Bar, RadarChart, Radar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';
import { api } from '../utils/api';

export default function Insights() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('overview');
  const [wellnessData, setWellnessData] = useState(null);
  const [personalityInsights, setPersonalityInsights] = useState(null);
  const [growthSummary, setGrowthSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAllInsights();
  }, []);

  const fetchAllInsights = async () => {
    try {
      setLoading(true);
      setError(null);

      const [wellnessRes, personalityRes, growthRes] = await Promise.all([
        api.get('/insights/wellness-overview'),
        api.get('/insights/personality-insights'),
        api.get('/insights/growth-summary')
      ]);

      setWellnessData(wellnessRes.data);
      setPersonalityInsights(personalityRes.data);
      setGrowthSummary(growthRes.data);
    } catch (err) {
      setError('Failed to load insights data');
      console.error('Insights error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 p-4 md:p-8">
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-64 bg-slate-800 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 p-4 md:p-8">
        <div className="bg-red-900 border border-red-700 rounded-lg p-4 text-red-100">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 p-4 md:p-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-slate-100 mb-2">
          ✨ Wellness Insights
        </h1>
        <p className="text-slate-400">Comprehensive view of your personal growth and wellness</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-4 mb-8 border-b border-slate-700">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-3 font-medium transition-colors ${
            activeTab === 'overview'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          📊 Overview
        </button>
        <button
          onClick={() => setActiveTab('personality')}
          className={`px-4 py-3 font-medium transition-colors ${
            activeTab === 'personality'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          🌟 Personality
        </button>
        <button
          onClick={() => setActiveTab('growth')}
          className={`px-4 py-3 font-medium transition-colors ${
            activeTab === 'growth'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          🎯 Growth
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && wellnessData && (
        <div className="space-y-6">
          {/* Personality Profile Card */}
          {wellnessData.personality && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-2xl font-bold text-slate-100 mb-4">🌟 Your Personality</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="text-lg font-semibold text-slate-100 mb-2">
                    {wellnessData.personality.archetype}
                  </div>
                  <div className="text-sm text-slate-400 mb-3">
                    Confidence: {Math.round(wellnessData.personality.confidence * 100)}%
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {wellnessData.personality.traits && Object.entries(wellnessData.personality.traits).map(([key, value]) => (
                      <span key={key} className="px-3 py-1 bg-slate-700 rounded-full text-sm text-slate-300">
                        {key}: {value.toFixed(1)}
                      </span>
                    ))}
                  </div>
                </div>
                {wellnessData.personality.traits && (
                  <ResponsiveContainer width="100%" height={250}>
                    <RadarChart data={Object.entries(wellnessData.personality.traits).map(([key, value]) => ({
                      name: key,
                      value: value * 10
                    }))}>
                      <PolarGrid stroke="#475569" />
                      <PolarAngleAxis dataKey="name" stroke="#94a3b8" />
                      <PolarRadiusAxis stroke="#94a3b8" angle={90} domain={[0, 10]} />
                      <Radar name="Trait Score" dataKey="value" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.6} />
                      <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
                    </RadarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          )}

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Goals Card */}
            {wellnessData.goals && (
              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="text-sm text-slate-400 mb-2">📌 Goals</div>
                <div className="text-3xl font-bold text-slate-100 mb-1">
                  {wellnessData.goals.active}/{wellnessData.goals.total}
                </div>
                <div className="text-sm text-slate-400">
                  {wellnessData.goals.completed} completed
                </div>
                <div className="mt-3 bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full transition-all"
                    style={{
                      width: `${(wellnessData.goals.completed / Math.max(wellnessData.goals.total, 1)) * 100}%`
                    }}
                  />
                </div>
              </div>
            )}

            {/* Habits Card */}
            {wellnessData.habits && (
              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="text-sm text-slate-400 mb-2">🔄 Habits</div>
                <div className="text-3xl font-bold text-slate-100 mb-1">
                  {wellnessData.habits.total}
                </div>
                <div className="text-sm text-slate-400">
                  {wellnessData.habits.max_streak} day streak
                </div>
                <div className="mt-3 bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    style={{
                      width: `${(wellnessData.habits.completion_rate || 0) * 100}%`
                    }}
                  />
                </div>
              </div>
            )}

            {/* Mood Card */}
            {wellnessData.mood && (
              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="text-sm text-slate-400 mb-2">😊 Mood</div>
                <div className="text-3xl font-bold text-slate-100 mb-1">
                  {(wellnessData.mood.average || 0).toFixed(1)}/10
                </div>
                <div className="text-sm text-slate-400">
                  {wellnessData.mood.trend === 'improving' ? '📈 Improving' : wellnessData.mood.trend === 'declining' ? '📉 Declining' : '➡️ Stable'}
                </div>
              </div>
            )}
          </div>

          {/* Recent Achievements */}
          {wellnessData.achievements && wellnessData.achievements.length > 0 && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-slate-100 mb-4">🏆 Recent Achievements</h3>
              <div className="space-y-2">
                {wellnessData.achievements.slice(0, 5).map((achievement, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-3 bg-slate-700 rounded-lg">
                    <span className="text-2xl">{achievement.badge}</span>
                    <div>
                      <div className="font-medium text-slate-100">{achievement.name}</div>
                      <div className="text-sm text-slate-400">{achievement.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Personality Tab */}
      {activeTab === 'personality' && personalityInsights && (
        <div className="space-y-6">
          {personalityInsights.personality && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-2xl font-bold text-slate-100 mb-4">{personalityInsights.personality.archetype}</h2>
              <p className="text-slate-300 mb-4">{personalityInsights.personality.description}</p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                {/* Strengths */}
                <div>
                  <h3 className="text-lg font-semibold text-slate-100 mb-3">💪 Strengths</h3>
                  <ul className="space-y-2">
                    {personalityInsights.personality.strengths?.map((strength, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-slate-300">
                        <span className="text-lg">✓</span>
                        <span>{strength}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Growth Areas */}
                <div>
                  <h3 className="text-lg font-semibold text-slate-100 mb-3">🌱 Growth Areas</h3>
                  <ul className="space-y-2">
                    {personalityInsights.personality.growth_areas?.map((area, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-slate-300">
                        <span className="text-lg">→</span>
                        <span>{area}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Recommended Goals */}
          {personalityInsights.recommended_goals && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-slate-100 mb-4">🎯 Recommended Goals</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {personalityInsights.recommended_goals.map((goal, idx) => (
                  <div key={idx} className="p-3 bg-slate-700 rounded-lg border border-slate-600">
                    <div className="font-medium text-slate-100">{goal}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommended Habits */}
          {personalityInsights.recommended_habits && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-slate-100 mb-4">🔄 Recommended Habits</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {personalityInsights.recommended_habits.map((habit, idx) => (
                  <div key={idx} className="p-3 bg-slate-700 rounded-lg border border-slate-600">
                    <div className="font-medium text-slate-100">{habit}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Growth Tab */}
      {activeTab === 'growth' && growthSummary && (
        <div className="space-y-6">
          {/* Goal Progress */}
          {growthSummary.goal_progress && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-2xl font-bold text-slate-100 mb-4">📊 Goal Progress</h2>
              <div className="space-y-4">
                {growthSummary.goal_progress.map((goal, idx) => (
                  <div key={idx}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-slate-300">{goal.name}</span>
                      <span className="text-sm text-slate-400">{Math.round(goal.progress)}%</span>
                    </div>
                    <div className="bg-slate-700 rounded-full h-3">
                      <div
                        className="bg-blue-500 h-3 rounded-full transition-all"
                        style={{ width: `${goal.progress}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Category Breakdown */}
          {growthSummary.category_breakdown && (
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-slate-100 mb-4">📈 Category Breakdown</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={Object.entries(growthSummary.category_breakdown).map(([category, count]) => ({
                  category,
                  count
                }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                  <XAxis dataKey="category" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
                  <Bar dataKey="count" fill="#3B82F6" name="Goals" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Completion Stats */}
          {growthSummary.completion_stats && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="text-sm text-slate-400 mb-2">✅ Completed</div>
                <div className="text-3xl font-bold text-green-400">{growthSummary.completion_stats.completed}</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="text-sm text-slate-400 mb-2">🔄 In Progress</div>
                <div className="text-3xl font-bold text-blue-400">{growthSummary.completion_stats.in_progress}</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="text-sm text-slate-400 mb-2">📋 Total</div>
                <div className="text-3xl font-bold text-slate-300">{growthSummary.completion_stats.total}</div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
