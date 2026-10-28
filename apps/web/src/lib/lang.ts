import { createContext, useContext } from "react";
import { useTranslation } from "react-i18next";

import type { Lang } from "@empire-t/api-client";

import { DEFAULT_LANG } from "../i18n";

/** The language of the current route (`/fr/...` or `/en/...`), set by the layout. */
export const LangContext = createContext<Lang>(DEFAULT_LANG);

export function useLang(): Lang {
  return useContext(LangContext);
}

/**
 * Translator bound to the route's language rather than i18next's global
 * language, so server rendering and client navigation never disagree.
 */
export function useT() {
  return useTranslation("translation", { lng: useLang() }).t;
}
