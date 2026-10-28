import i18next, { type i18n as I18n } from "i18next";
import { initReactI18next } from "react-i18next";

import type { Lang } from "@empire-t/api-client";

import en from "./en";
import fr from "./fr";

export const LANGS = ["fr", "en"] as const satisfies readonly Lang[];
export const DEFAULT_LANG: Lang = "fr";

export function isLang(value: unknown): value is Lang {
  return value === "fr" || value === "en";
}

/** BCP 47 locale for Intl formatting and `og:locale`. */
export const LOCALES: Record<Lang, string> = { fr: "fr-CM", en: "en-CM" };

/**
 * One instance per render on the server, one per page load in the browser.
 * Both languages are bundled (about 8 KB gzipped together), so switching is
 * instant and initialisation is synchronous: no flash of untranslated keys.
 */
export function createI18n(lang: Lang): I18n {
  const instance = i18next.createInstance();
  void instance.use(initReactI18next).init({
    lng: lang,
    fallbackLng: DEFAULT_LANG,
    supportedLngs: LANGS,
    resources: { fr: { translation: fr }, en: { translation: en } },
    interpolation: { escapeValue: false },
    initAsync: false,
    returnNull: false,
  });
  return instance;
}
