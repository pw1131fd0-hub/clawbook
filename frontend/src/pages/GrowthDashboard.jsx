import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { api } from '../utils/api';
import AchievementCard from '../components/AchievementCard';

const COLORS = {
  personal: '#3B82F6',
  professional: '#10B981',
  health: '#F59E0B',
  learning: '#8B5CF6',
  active: '#22C55E',
  completed: '#0EA5E9',
};

export default function GrowthDashboard() {
  const { t } = useTranslation();
  const [goals, setGoals] = useState([]);
  const [achievements, setAchievements] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showGoalForm, setShowGoalForm] = useState(false);
  const [newGoal, setNewGoal] = useState({
    title: '',
    description: '',
    category: 'personal',
    target_value: 10,
    unit: '',
  });

  useEffect(() => {
    fetchGoalsAndInsights();
  }, []);

  const fetchGoalsAndInsights = async () => {
    try {
      setLoading(true);
      setError(null);

      const [goalsRes, insightsRes, achievementsRes] = await Promise.all([
        api.get('/growth/goals'),
        api.get('/growth/insights'),
        api.get('/growth/achievements').catch(() => ({ data: [] })) // Graceful fallback
      ]);

      setGoals(goalsRes.data || []);
      setInsights(insightsRes.data);
      setAchievements(achievementsRes.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load growth data');
      console.error('Growth data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGoal = async (e) => {
    e.preventDefault();
    if (!newGoal.title || newGoal.target_value <= 0) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setError(null);
      await api.post('/growth/goals', newGoal);
      setNewGoal({
        title: '',
        description: '',
        category: 'personal',
        target_value: 10,
        unit: '',
      });
      setShowGoalForm(false);
      await fetchGoalsAndInsights();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create goal');
    }
  };

  const handleDeleteGoal = async (goalId) => {
    if (!window.confirm('Are you sure you want to delete this goal?')) return;

    try {
      setError(null);
      await api.delete(`/growth/goals/${goalId}`);
      await fetchGoalsAndInsights();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete goal');
    }
  };

  const getProgressPercentage = (goal) => {
    if (goal.target_value <= 0) return 0;
    return Math.min(100, (goal.current_value / goal.target_value) * 100);
  };

  const getCategoryBreakdownData = () => {
    if (!insights?.category_breakdown) return [];
    return Object.entries(insights.category_breakdown).map(([category, data]) => ({
      name: category,
      value: data.total,
      completed: data.completed,
      ...data
    }));
  };

  const getGoalStatusData = () => {
    if (!insights) return [];
    return [
      { name: 'Active', value: insights.active_goals, fill: COLORS.active },
      { name: 'Completed', value: insights.completed_goals, fill: COLORS.completed },
    ];
  };

  if (loading && goals.length === 0) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-blue-400">🎯 Growth Tracking Dashboard</h1>
          <button
            onClick={() => setShowGoalForm(!showGoalForm)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
          >
            {showGoalForm ? '✕ Cancel' : '+ New Goal'}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Goal Creation Form */}
        {showGoalForm && (
          <form onSubmit={handleCreateGoal} className="bg-slate-800 rounded-lg p-6 mb-8 border border-slate-700">
            <h2 className="text-xl font-semibold mb-4">Create New Goal</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Goal Title"
                value={newGoal.title}
                onChange={(e) => setNewGoal({...newGoal, title: e.target.value})}
                className="bg-slate-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <select
                value={newGoal.category}
                onChange={(e) => setNewGoal({...newGoal, category: e.target.value})}
                className="bg-slate-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="personal">Personal</option>
                <option value="professional">Professional</option>
                <option value="health">Health</option>
                <option value="learning">Learning</option>
              </select>
              <input
                type="number"
                placeholder="Target Value"
                value={newGoal.target_value}
                onChange={(e) => setNewGoal({...newGoal, target_value: parseInt(e.target.value) || 1})}
                className="bg-slate-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="text"
                placeholder="Unit (e.g., hours, pages)"
                value={newGoal.unit}
                onChange={(e) => setNewGoal({...newGoal, unit: e.target.value})}
                className="bg-slate-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <textarea
                placeholder="Description (optional)"
                value={newGoal.description}
                onChange={(e) => setNewGoal({...newGoal, description: e.target.value})}
                className="bg-slate-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 col-span-2"
                rows="3"
              />
            </div>
            <button
              type="submit"
              className="mt-4 bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition-colors"
            >
              Create Goal
            </button>
          </form>
        )}

        {/* Insights Summary */}
        {insights && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <div className="text-sm text-slate-400">Total Goals</div>
              <div className="text-3xl font-bold text-blue-400">{insights.total_goals}</div>
            </div>
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <div className="text-sm text-slate-400">Completion Rate</div>
              <div className="text-3xl font-bold text-green-400">{insights.completion_rate}%</div>
            </div>
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <div className="text-sm text-slate-400">Total Achievements</div>
              <div className="text-3xl font-bold text-purple-400">{insights.total_achievements}</div>
            </div>
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <div className="text-sm text-slate-400">Active Goals</div>
              <div className="text-3xl font-bold text-amber-400">{insights.active_goals}</div>
            </div>
          </div>
        )}

        {/* Charts Section */}
        {insights && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Goal Status Pie Chart */}
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-lg font-semibold mb-4">Goal Status</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={getGoalStatusData()}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {getGoalStatusData().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Category Breakdown Bar Chart */}
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-lg font-semibold mb-4">Goals by Category</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={getCategoryBreakdownData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                  <XAxis dataKey="name" stroke="#94A3B8" />
                  <YAxis stroke="#94A3B8" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #475569', borderRadius: '8px' }}
                    labelStyle={{ color: '#F1F5F9' }}
                  />
                  <Legend />
                  <Bar dataKey="value" fill="#3B82F6" name="Total" />
                  <Bar dataKey="completed" fill="#10B981" name="Completed" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Goals List */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h2 className="text-xl font-semibold mb-6">Your Goals</h2>
          {goals.length === 0 ? (
            <div className="text-center py-12 text-slate-400">
              <p>No goals yet. Create one to start tracking your growth!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {goals.map((goal) => {
                const progress = getProgressPercentage(goal);
                return (
                  <div key={goal.id} className="bg-slate-700 rounded-lg p-6 border border-slate-600 hover:border-slate-500 transition-colors">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-white">{goal.title}</h3>
                        <div className="flex gap-2 mt-2">
                          <span className="px-2 py-1 bg-slate-600 rounded text-xs text-slate-300 capitalize">{goal.category}</span>
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${goal.status === 'completed' ? 'bg-green-900 text-green-200' : 'bg-blue-900 text-blue-200'}`}>
                            {goal.status === 'completed' ? '✓ Completed' : 'Active'}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteGoal(goal.id)}
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        Delete
                      </button>
                    </div>

                    {goal.description && (
                      <p className="text-slate-300 text-sm mb-4">{goal.description}</p>
                    )}

                    <div className="mb-4">
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-slate-300">Progress</span>
                        <span className="text-blue-400 font-semibold">
                          {goal.current_value}/{goal.target_value} {goal.unit}
                        </span>
                      </div>
                      <div className="w-full bg-slate-600 rounded-full h-3 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-purple-500 h-full rounded-full transition-all duration-500"
                          style={{ width: `${progress}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="text-xs text-slate-400">
                      {progress === 100 ? (
                        <span className="text-green-400">✓ Goal completed!</span>
                      ) : (
                        <span>{progress.toFixed(0)}% complete</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Achievements & Milestones Section - Milestone 3 */}
        {achievements && achievements.length > 0 && (
          <div className="mt-8">
            <h2 className="text-2xl font-bold text-amber-300 mb-6">🏆 Achievements & Milestones</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {achievements.map((achievement) => {
                const goalForAchievement = goals.find(g => g.id === achievement.goal_id);
                return (
                  <AchievementCard
                    key={achievement.id}
                    achievement={achievement}
                    goal={goalForAchievement}
                  />
                );
              })}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {insights?.recommended_next_actions && insights.recommended_next_actions.length > 0 && (
          <div className="mt-8 bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h2 className="text-lg font-semibold mb-4">💡 Recommendations</h2>
            <ul className="space-y-2">
              {insights.recommended_next_actions.map((action, index) => (
                <li key={index} className="flex items-start gap-3 text-slate-300">
                  <span className="text-yellow-400">→</span>
                  <span>{action}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
