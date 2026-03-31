import React, { useState, useEffect } from 'react';
import { fetchPosts } from '../utils/api';

const MOOD_COLORS = {
  '😊': '#10b981', // green
  '😐': '#6b7280', // gray
  '😔': '#ef4444', // red
  '🥰': '#f43f5e', // pink
  '💭': '#3b82f6', // blue
  '🎯': '#f59e0b', // amber
  '🙏': '#8b5cf6', // purple
  '💪': '#ec4899', // rose
  '😴': '#0ea5e9', // cyan
  '😤': '#f97316', // orange
};

const MOOD_LABELS = {
  '😊': 'Happy',
  '😐': 'Neutral',
  '😔': 'Sad',
  '🥰': 'Grateful',
  '💭': 'Thoughtful',
  '🎯': 'Ambitious',
  '🙏': 'Thankful',
  '💪': 'Strong',
  '😴': 'Tired',
  '😤': 'Frustrated',
};

export default function EmotionTrendsChart() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPostsData();
  }, []);

  const fetchPostsData = async () => {
    try {
      setLoading(true);
      const response = await fetchPosts(100, 0);
      setPosts(response.posts || []);
    } catch (err) {
      setError('Failed to load emotion data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 bg-slate-800 dark:bg-slate-800 rounded-lg text-center text-slate-400">
        Loading emotion trends...
      </div>
    );
  }

  if (posts.length === 0) {
    return (
      <div className="p-6 bg-slate-800 dark:bg-slate-800 rounded-lg text-center text-slate-400">
        No posts yet. Start journaling to see your emotion trends!
      </div>
    );
  }

  // Calculate mood distribution
  const moodCounts = posts.reduce((acc, post) => {
    acc[post.mood] = (acc[post.mood] || 0) + 1;
    return acc;
  }, {});

  const sortedMoods = Object.entries(moodCounts).sort((a, b) => b[1] - a[1]);
  const totalMoods = Object.values(moodCounts).reduce((a, b) => a + b, 0);

  // Get recent moods (last 30 posts) for timeline
  const recentPosts = posts.slice(0, 30).reverse();
  const maxCount = Math.max(...sortedMoods.map(([_, count]) => count));

  // Calculate mood percentage
  const getMoodPercentage = (mood) => {
    return ((moodCounts[mood] || 0) / totalMoods * 100).toFixed(1);
  };

  // Most common mood
  const topMood = sortedMoods[0] ? sortedMoods[0][0] : null;
  const topMoodCount = sortedMoods[0] ? sortedMoods[0][1] : 0;

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 bg-slate-800 dark:bg-slate-800 rounded-lg border border-slate-700">
          <div className="text-sm text-slate-400 mb-1">Total Entries</div>
          <div className="text-2xl font-bold text-slate-100">{totalMoods}</div>
        </div>

        <div className="p-4 bg-slate-800 dark:bg-slate-800 rounded-lg border border-slate-700">
          <div className="text-sm text-slate-400 mb-1">Top Mood</div>
          <div className="text-2xl">
            {topMood}
            <span className="text-sm text-slate-400 ml-2">({topMoodCount}x)</span>
          </div>
        </div>

        <div className="p-4 bg-slate-800 dark:bg-slate-800 rounded-lg border border-slate-700">
          <div className="text-sm text-slate-400 mb-1">Unique Moods</div>
          <div className="text-2xl font-bold text-slate-100">{sortedMoods.length}</div>
        </div>

        <div className="p-4 bg-slate-800 dark:bg-slate-800 rounded-lg border border-slate-700">
          <div className="text-sm text-slate-400 mb-1">Avg per Day</div>
          <div className="text-2xl font-bold text-slate-100">
            {(totalMoods / Math.max(1, Math.ceil(recentPosts.length / 7))).toFixed(1)}
          </div>
        </div>
      </div>

      {/* Mood Distribution Bar Chart */}
      <div className="p-4 bg-slate-800 dark:bg-slate-800 rounded-lg border border-slate-700">
        <h3 className="text-lg font-semibold text-slate-100 mb-4">Emotion Distribution</h3>
        <div className="space-y-3">
          {sortedMoods.map(([mood, count]) => (
            <div key={mood} className="flex items-center gap-3">
              <span className="text-2xl w-8">{mood}</span>
              <div className="flex-1">
                <div className="bg-slate-700 rounded-full h-8 overflow-hidden">
                  <div
                    className="h-full transition-all duration-300 flex items-center justify-end pr-2 text-xs font-semibold text-white"
                    style={{
                      width: `${(count / maxCount) * 100}%`,
                      backgroundColor: MOOD_COLORS[mood],
                    }}
                  >
                    {count > 0 && count}
                  </div>
                </div>
              </div>
              <div className="w-16 text-right">
                <span className="text-sm text-slate-400">
                  {getMoodPercentage(mood)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Timeline of Recent Moods */}
      <div className="p-4 bg-slate-800 dark:bg-slate-800 rounded-lg border border-slate-700">
        <h3 className="text-lg font-semibold text-slate-100 mb-4">Recent Mood Timeline</h3>
        <div className="flex justify-between items-end h-40 gap-1 px-2">
          {recentPosts.map((post, idx) => {
            const moodCount = moodCounts[post.mood] || 1;
            const heightPercent = (moodCount / maxCount) * 100;
            return (
              <div
                key={`${post.id}-${idx}`}
                className="flex-1 flex flex-col items-center gap-1 group cursor-pointer"
                title={`${post.mood} ${MOOD_LABELS[post.mood]}`}
              >
                <div
                  className="w-full rounded-t transition-all duration-200 hover:opacity-80"
                  style={{
                    height: `${Math.max(heightPercent, 10)}%`,
                    backgroundColor: MOOD_COLORS[post.mood],
                  }}
                />
                <span className="text-xs text-slate-500 group-hover:text-slate-300 transition-colors">
                  {post.mood}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-900 bg-opacity-30 border border-red-700 rounded-lg text-red-400">
          {error}
        </div>
      )}
    </div>
  );
}
