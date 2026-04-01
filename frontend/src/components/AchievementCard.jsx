import React from 'react';
import { useTranslation } from 'react-i18next';

/**
 * AchievementCard - Displays achievement or milestone with celebration animation.
 * Milestone 3 deliverable for v1.7 Phase 3: Growth Tracking Dashboard
 */
export default function AchievementCard({ achievement, goal }) {
  const { t } = useTranslation();

  // Format date to readable format
  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return 'Unknown date';
    }
  };

  // Get achievement type icon
  const getAchievementIcon = (title) => {
    if (!title) return '🎯';
    const lower = title.toLowerCase();
    if (lower.includes('milestone') || lower.includes('50%')) return '🎉';
    if (lower.includes('complete') || lower.includes('100%')) return '✨';
    if (lower.includes('first')) return '🚀';
    if (lower.includes('streak')) return '🔥';
    if (lower.includes('goal')) return '🏆';
    return '⭐';
  };

  // Celebrate achievement with animation
  const celebrateAchievement = () => {
    // Create confetti-like visual effect by animating several particles
    const container = document.querySelector(`#achievement-${achievement.id}`);
    if (!container) return;

    // Add celebration animation class
    container.classList.add('achievement-celebrate');

    // Create floating particles
    for (let i = 0; i < 8; i++) {
      const particle = document.createElement('div');
      particle.className = 'achievement-particle';
      particle.textContent = getAchievementIcon(achievement.title);
      particle.style.left = Math.random() * 100 + '%';
      particle.style.animation = `float-up ${1 + Math.random() * 1}s ease-out forwards`;
      container.appendChild(particle);

      setTimeout(() => particle.remove(), 1500);
    }

    // Remove animation class after it completes
    setTimeout(() => {
      container.classList.remove('achievement-celebrate');
    }, 300);
  };

  const categoryColors = {
    personal: 'from-blue-600 to-blue-400',
    professional: 'from-green-600 to-green-400',
    health: 'from-yellow-600 to-yellow-400',
    learning: 'from-purple-600 to-purple-400',
  };

  const goalCategory = goal?.category || 'personal';
  const gradientClass = categoryColors[goalCategory] || 'from-slate-600 to-slate-400';

  return (
    <div
      id={`achievement-${achievement.id}`}
      className="relative bg-gradient-to-r from-slate-800 to-slate-750 rounded-lg p-6 border-2 border-amber-500 shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden"
    >
      {/* Achievement Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-4">
          <div className="text-4xl">{getAchievementIcon(achievement.title)}</div>
          <div>
            <h3 className="text-xl font-bold text-amber-300">
              {achievement.title || 'Achievement Unlocked'}
            </h3>
            <p className="text-sm text-slate-400">
              {goal ? `Goal: ${goal.title}` : 'Milestone Achievement'}
            </p>
          </div>
        </div>
        <button
          onClick={celebrateAchievement}
          className="text-lg hover:scale-110 transition-transform cursor-pointer"
          title="Celebrate this achievement"
        >
          🎉
        </button>
      </div>

      {/* Achievement Details */}
      {achievement.description && (
        <p className="text-slate-300 mb-4 text-sm">
          {achievement.description}
        </p>
      )}

      {/* Progress Value Display */}
      {achievement.progress_value !== undefined && (
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-slate-300">Progress</span>
            <span className="text-sm font-bold text-amber-300">
              {achievement.progress_value}
              {goal?.unit ? ` ${goal.unit}` : ''}
            </span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full bg-gradient-to-r ${gradientClass} rounded-full transition-all duration-500`}
              style={{
                width: goal
                  ? `${Math.min(100, (achievement.progress_value / goal.target_value) * 100)}%`
                  : '100%',
              }}
            />
          </div>
        </div>
      )}

      {/* Achievement Date */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-700">
        <span className="text-xs text-slate-500 uppercase tracking-wide">
          {t('growth.achieved_on', 'Achieved on')}
        </span>
        <span className="text-sm font-semibold text-amber-200">
          {formatDate(achievement.achieved_date)}
        </span>
      </div>

      {/* Celebration Status */}
      {achievement.celebration_sent && (
        <div className="mt-3 flex items-center gap-2 text-xs text-amber-300">
          <span>✓ Celebrated</span>
        </div>
      )}

      {/* CSS for particle animations */}
      <style>{`
        @keyframes float-up {
          0% {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
          100% {
            opacity: 0;
            transform: translateY(-50px) scale(0.5);
          }
        }

        .achievement-particle {
          position: absolute;
          font-size: 2rem;
          pointer-events: none;
          z-index: 10;
        }

        #achievement-${achievement.id}.achievement-celebrate {
          animation: pulse-celebrate 0.3s ease-out;
        }

        @keyframes pulse-celebrate {
          0% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.05);
          }
          100% {
            transform: scale(1);
          }
        }
      `}</style>
    </div>
  );
}
