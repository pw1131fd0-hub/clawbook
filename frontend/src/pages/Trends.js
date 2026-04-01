import React from 'react';
import { useTranslation } from 'react-i18next';
import EmotionTrendsChart from '../components/EmotionTrendsChart';

export default function Trends() {
  const { t } = useTranslation();

  return (
    <main className="flex-1 max-w-4xl mx-auto min-h-screen">
      <div className="sticky top-16 z-30 border-b border-slate-800 dark:border-slate-700 bg-slate-900/95 dark:bg-slate-900/95 backdrop-blur px-6 py-4">
        <h1 className="text-2xl font-bold text-slate-100 dark:text-slate-100">
          📊 {t('page.trends.title')}
        </h1>
        <p className="text-sm text-slate-400 dark:text-slate-400 mt-1">
          {t('page.trends.subtitle')}
        </p>
      </div>

      <div className="p-6 space-y-6">
        <EmotionTrendsChart />
      </div>
    </main>
  );
}
