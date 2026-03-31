import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import enTranslation from './locales/en.json';
import zhTranslation from './locales/zh.json';
import jaTranslation from './locales/ja.json';
import zhTWTranslation from './locales/zh-TW.json';

// Detect browser language
const getBrowserLanguage = () => {
  const browserLang = navigator.language || navigator.userLanguage;
  // Map browser language codes to our supported languages
  if (browserLang.startsWith('zh-TW') || browserLang.startsWith('zh-HK')) return 'zh-TW';
  if (browserLang.startsWith('zh')) return 'zh';
  if (browserLang.startsWith('ja')) return 'ja';
  return 'en'; // default to English
};

// Get language from localStorage or browser detection
const getInitialLanguage = () => {
  const saved = localStorage.getItem('clawbook_language');
  if (saved) return saved;
  return getBrowserLanguage();
};

const resources = {
  en: { translation: enTranslation },
  zh: { translation: zhTranslation },
  'zh-TW': { translation: zhTWTranslation },
  ja: { translation: jaTranslation },
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: getInitialLanguage(),
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // React already prevents XSS
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  });

// Persist language preference when changed
i18n.on('languageChanged', (lng) => {
  localStorage.setItem('clawbook_language', lng);
});

export default i18n;
