import { Navigate } from "react-router";

import { DEFAULT_LANG } from "../i18n";

/** `/` in development picks the visitor's language; nginx does the same in production. */
export function LanguageRedirect() {
  const languages = typeof navigator === "undefined" ? [] : navigator.languages;
  const prefersEnglish =
    languages.some((code) => code.toLowerCase().startsWith("en")) &&
    !languages.some((code) => code.toLowerCase().startsWith("fr"));
  return <Navigate to={`/${prefersEnglish ? "en" : DEFAULT_LANG}/`} replace />;
}
