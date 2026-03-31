import React from 'react';
import { useTranslation } from 'react-i18next';

/**
 * Language Switcher Component
 * Allows users to switch between supported languages:
 * - English (en)
 * - 简体中文 (zh)
 * - 繁體中文 (zh-TW)
 * - 日本語 (ja)
 */
const LanguageSwitcher = ({ className = '' }) => {
  const { i18n } = useTranslation();

  const languages = [
    { code: 'en', name: 'English', flag: '🌍' },
    { code: 'zh', name: '简体中文', flag: '🇨🇳' },
    { code: 'zh-TW', name: '繁體中文', flag: '🇹🇼' },
    { code: 'ja', name: '日本語', flag: '🇯🇵' },
  ];

  const handleLanguageChange = (langCode) => {
    i18n.changeLanguage(langCode);
  };

  return (
    <div className={`language-switcher ${className}`}>
      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-slate-300">Language:</label>
        <select
          value={i18n.language}
          onChange={(e) => handleLanguageChange(e.target.value)}
          className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-100 hover:border-slate-600 focus:outline-none focus:ring-2 focus:ring-red-500 transition-colors"
        >
          {languages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.flag} {lang.name}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default LanguageSwitcher;
