import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../utils/api';

export default function Recommendations() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('goals');
  const [goalRecs, setGoalRecs] = useState(null);
  const [habitRecs, setHabitRecs] = useState(null);
  const [weeklyFocus, setWeeklyFocus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAllRecommendations();
  }, []);

  const fetchAllRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);

      const [goalsRes, habitsRes, weeklyRes] = await Promise.all([
        api.get('/recommendations/goals'),
        api.get('/recommendations/habits'),
        api.get('/recommendations/weekly-focus')
      ]);

      setGoalRecs(goalsRes.data);
      setHabitRecs(habitsRes.data);
      setWeeklyFocus(weeklyRes.data);
    } catch (err) {
      setError('Failed to load recommendations data');
      console.error('Recommendations error:', err);
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
          💡 Personalized Recommendations
        </h1>
        <p className="text-slate-400">Custom suggestions based on your personality and current state</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-4 mb-8 border-b border-slate-700 flex-wrap">
        <button
          onClick={() => setActiveTab('goals')}
          className={`px-4 py-3 font-medium transition-colors ${
            activeTab === 'goals'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          🎯 Goal Ideas
        </button>
        <button
          onClick={() => setActiveTab('habits')}
          className={`px-4 py-3 font-medium transition-colors ${
            activeTab === 'habits'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          🔄 Habit Builder
        </button>
        <button
          onClick={() => setActiveTab('weekly')}
          className={`px-4 py-3 font-medium transition-colors ${
            activeTab === 'weekly'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-300'
          }`}
        >
          📅 This Week
        </button>
      </div>

      {/* Goal Recommendations */}
      {activeTab === 'goals' && goalRecs && (
        <div className="space-y-6">
          {goalRecs.by_category && Object.entries(goalRecs.by_category).map(([category, goals]) => (
            <div key={category} className="space-y-3">
              <h2 className="text-2xl font-bold text-slate-100 capitalize">{category}</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {goals.map((goal, idx) => (
                  <div
                    key={idx}
                    className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-blue-500 transition-colors cursor-pointer"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-slate-100">{goal.name}</h3>
                        <p className="text-sm text-slate-400 mt-1">{goal.description}</p>
                      </div>
                      {goal.priority && (
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          goal.priority === 'high' ? 'bg-red-900 text-red-200' :
                          goal.priority === 'medium' ? 'bg-yellow-900 text-yellow-200' :
                          'bg-green-900 text-green-200'
                        }`}>
                          {goal.priority}
                        </span>
                      )}
                    </div>
                    {goal.why && (
                      <div className="text-sm text-slate-300 p-3 bg-slate-700 rounded mt-3">
                        💭 {goal.why}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Habit Recommendations */}
      {activeTab === 'habits' && habitRecs && (
        <div className="space-y-6">
          {habitRecs.habit_templates && (
            <div>
              <h2 className="text-2xl font-bold text-slate-100 mb-4">Recommended Habits</h2>
              <div className="space-y-4">
                {habitRecs.habit_templates.map((habit, idx) => (
                  <div
                    key={idx}
                    className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-blue-500 transition-colors cursor-pointer"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-slate-100">{habit.name}</h3>
                        <p className="text-sm text-slate-400 mt-1">{habit.description}</p>
                      </div>
                      {habit.difficulty && (
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          habit.difficulty === 'easy' ? 'bg-green-900 text-green-200' :
                          habit.difficulty === 'medium' ? 'bg-yellow-900 text-yellow-200' :
                          'bg-red-900 text-red-200'
                        }`}>
                          {habit.difficulty}
                        </span>
                      )}
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-sm mt-3">
                      {habit.frequency && (
                        <div className="p-2 bg-slate-700 rounded">
                          <span className="text-slate-400">Frequency:</span>
                          <span className="text-slate-100 ml-2">{habit.frequency}</span>
                        </div>
                      )}
                      {habit.category && (
                        <div className="p-2 bg-slate-700 rounded">
                          <span className="text-slate-400">Category:</span>
                          <span className="text-slate-100 ml-2">{habit.category}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Gap-Based Recommendations */}
          {habitRecs.gap_based_recommendations && (
            <div>
              <h2 className="text-2xl font-bold text-slate-100 mb-4">💡 Fill These Gaps</h2>
              <div className="space-y-4">
                {habitRecs.gap_based_recommendations.map((gap, idx) => (
                  <div
                    key={idx}
                    className="bg-slate-800 rounded-lg p-6 border border-slate-700 border-l-4 border-l-blue-500"
                  >
                    <h3 className="text-lg font-semibold text-slate-100 mb-2">{gap.title}</h3>
                    <p className="text-slate-300">{gap.suggestion}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Weekly Focus */}
      {activeTab === 'weekly' && weeklyFocus && (
        <div className="space-y-6">
          {/* Alert Sections */}
          {(weeklyFocus.low_mood_alert || weeklyFocus.stalled_goals || weeklyFocus.habit_streaks) && (
            <div className="space-y-4">
              {weeklyFocus.low_mood_alert && (
                <div className="bg-yellow-900 border border-yellow-700 rounded-lg p-4 text-yellow-100">
                  <h3 className="font-semibold mb-2">😟 Mood Check-In Needed</h3>
                  <p>{weeklyFocus.low_mood_alert}</p>
                </div>
              )}

              {weeklyFocus.stalled_goals && weeklyFocus.stalled_goals.length > 0 && (
                <div className="bg-orange-900 border border-orange-700 rounded-lg p-4 text-orange-100">
                  <h3 className="font-semibold mb-2">🎯 Goals That Need Attention</h3>
                  <ul className="space-y-1">
                    {weeklyFocus.stalled_goals.map((goal, idx) => (
                      <li key={idx}>• {goal}</li>
                    ))}
                  </ul>
                </div>
              )}

              {weeklyFocus.habit_streaks && weeklyFocus.habit_streaks.length > 0 && (
                <div className="bg-red-900 border border-red-700 rounded-lg p-4 text-red-100">
                  <h3 className="font-semibold mb-2">🔄 Habits at Risk</h3>
                  <p className="text-sm mb-2">Keep your streaks alive this week:</p>
                  <ul className="space-y-1">
                    {weeklyFocus.habit_streaks.map((habit, idx) => (
                      <li key={idx}>• {habit}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Weekly Focus Areas */}
          {weeklyFocus.focus_areas && weeklyFocus.focus_areas.length > 0 && (
            <div>
              <h2 className="text-2xl font-bold text-slate-100 mb-4">🎯 This Week's Focus</h2>
              <div className="space-y-3">
                {weeklyFocus.focus_areas.map((area, idx) => (
                  <div
                    key={idx}
                    className="bg-slate-800 rounded-lg p-4 border border-slate-700"
                  >
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">
                        {area.includes('learning') ? '📚' :
                         area.includes('rest') ? '😴' :
                         area.includes('health') ? '💪' :
                         area.includes('relationship') ? '❤️' :
                         area.includes('creativity') ? '🎨' :
                         '⭐'}
                      </div>
                      <span className="text-slate-100">{area}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Items */}
          {weeklyFocus.action_items && weeklyFocus.action_items.length > 0 && (
            <div>
              <h2 className="text-2xl font-bold text-slate-100 mb-4">✅ Action Items</h2>
              <div className="space-y-2">
                {weeklyFocus.action_items.map((item, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-3 p-4 bg-slate-800 rounded-lg border border-slate-700 cursor-pointer hover:border-blue-500 transition-colors"
                  >
                    <input
                      type="checkbox"
                      className="w-5 h-5 rounded border-slate-600 cursor-pointer"
                    />
                    <span className="text-slate-100">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
