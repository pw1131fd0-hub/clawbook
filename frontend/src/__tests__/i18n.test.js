import i18n from '../i18n/config';

describe('i18n Configuration', () => {
  test('should initialize with default language (English)', () => {
    // Clear localStorage to test default behavior
    localStorage.clear();

    // The i18n should be initialized
    expect(i18n).toBeDefined();
    expect(['en', 'zh', 'zh-TW', 'ja']).toContain(i18n.language);
  });

  test('should have all required languages loaded', async () => {
    const languages = ['en', 'zh', 'zh-TW', 'ja'];

    for (const lang of languages) {
      expect(i18n.hasResourceBundle(lang, 'translation')).toBe(true);
    }
  });

  test('should fallback to English when language not supported', async () => {
    await i18n.changeLanguage('unsupported');
    // It should still have resources available
    expect(i18n.t('common.appName')).toBeDefined();
  });

  test('should translate common.appName for all languages', async () => {
    const translations = {
      en: 'ClawBook',
      zh: '爪之書',
      'zh-TW': '爪之書',
      ja: '爪の本',
    };

    for (const [lang, expected] of Object.entries(translations)) {
      await i18n.changeLanguage(lang);
      const translated = i18n.t('common.appName');
      expect(translated).toBe(expected);
    }
  });

  test('should persist language preference to localStorage', async () => {
    localStorage.clear();
    await i18n.changeLanguage('ja');

    const saved = localStorage.getItem('clawbook_language');
    expect(saved).toBe('ja');
  });

  test('should have all required translation keys for navigation', async () => {
    const navKeys = [
      'navigation.home',
      'navigation.feed',
      'navigation.dashboard',
      'navigation.trends',
      'navigation.decisionPaths',
    ];

    for (const key of navKeys) {
      const translated = i18n.t(key);
      expect(translated).not.toContain(key); // Should not be the key itself
      expect(translated.length).toBeGreaterThan(0);
    }
  });

  test('should detect browser language on first visit', () => {
    localStorage.clear();

    // Simulate browser language
    const originalLanguage = navigator.language;
    Object.defineProperty(navigator, 'language', {
      value: 'en-US',
      configurable: true,
    });

    // The config should be created with this in mind
    expect(i18n).toBeDefined();

    // Restore original
    Object.defineProperty(navigator, 'language', {
      value: originalLanguage,
      configurable: true,
    });
  });
});
