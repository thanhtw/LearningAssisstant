export const APP_LANGUAGE_STORAGE_KEY = 'nova-language';

export const SUPPORTED_LANGUAGES = {
  en: {
    locale: 'en-US',
    voicePrefixes: ['en'],
  },
  'zh-TW': {
    locale: 'zh-TW',
    voicePrefixes: ['zh-tw', 'zh-hk', 'zh-hant', 'zh'],
  },
  vi: {
    locale: 'vi-VN',
    voicePrefixes: ['vi'],
  },
} as const;

export type AppLanguage = keyof typeof SUPPORTED_LANGUAGES;

export const DEFAULT_LANGUAGE: AppLanguage = 'en';

export function isAppLanguage(value: string | null | undefined): value is AppLanguage {
  return Boolean(value && value in SUPPORTED_LANGUAGES);
}

export function resolveAppLanguage(value: string | null | undefined): AppLanguage {
  if (!value) {
    return DEFAULT_LANGUAGE;
  }

  if (isAppLanguage(value)) {
    return value;
  }

  const normalized = value.toLowerCase();
  if (normalized.startsWith('zh')) {
    return 'zh-TW';
  }
  if (normalized.startsWith('vi')) {
    return 'vi';
  }

  return DEFAULT_LANGUAGE;
}

export function getInitialLanguage(): AppLanguage {
  if (typeof window === 'undefined') {
    return DEFAULT_LANGUAGE;
  }

  return resolveAppLanguage(
    window.localStorage.getItem(APP_LANGUAGE_STORAGE_KEY) || window.navigator.language
  );
}

export function getSpeechLocale(language: AppLanguage): string {
  return SUPPORTED_LANGUAGES[language].locale;
}

export function getVoiceLanguagePrefixes(language: AppLanguage): readonly string[] {
  return SUPPORTED_LANGUAGES[language].voicePrefixes;
}
