import type { Lang } from "@empire-t/api-client";

/**
 * Localised URL segments. French URLs read naturally to French-speaking
 * customers and rank for French searches; the English site mirrors them.
 * Every page has the same id in both languages so the toggle can map
 * `/fr/reserver` to `/en/book` without a lookup table elsewhere.
 */
export const PAGE_SEGMENTS = {
  home: { fr: "", en: "" },
  about: { fr: "a-propos", en: "about" },
  services: { fr: "services", en: "services" },
  gallery: { fr: "galerie", en: "gallery" },
  careers: { fr: "recrutement", en: "careers" },
  book: { fr: "reserver", en: "book" },
  contact: { fr: "contact", en: "contact" },
} as const satisfies Record<string, Record<Lang, string>>;

export type PageId = keyof typeof PAGE_SEGMENTS;
export const PAGE_IDS = Object.keys(PAGE_SEGMENTS) as PageId[];

/** `/fr/`, `/fr/a-propos`, `/en/services/men`... Home keeps its trailing slash. */
export function pathFor(page: PageId, lang: Lang, subPath?: string): string {
  const segment = PAGE_SEGMENTS[page][lang];
  const base = segment ? `/${lang}/${segment}` : `/${lang}/`;
  return subPath ? `${base}/${encodeURIComponent(subPath)}` : base;
}

export function servicesPath(lang: Lang, category?: string): string {
  return pathFor("services", lang, category);
}

export interface BookingPrefill {
  service?: string | undefined;
  date?: string | undefined;
  time?: string | undefined;
  phone?: string | undefined;
}

/** Booking page with the quick-bar or "Réserver" values carried over in the query string. */
export function bookingPath(lang: Lang, prefill: BookingPrefill = {}): string {
  const params = new URLSearchParams();
  for (const key of ["service", "date", "time", "phone"] as const) {
    const value = prefill[key];
    if (value) params.set(key, value);
  }
  const query = params.toString();
  return query ? `${pathFor("book", lang)}?${query}` : pathFor("book", lang);
}

/** The same page in the other language, keeping any sub-path (services tab) and query. */
export function translatePath(pathname: string, search: string, to: Lang): string {
  const [, from, segment = "", ...rest] = pathname.split("/");
  const page = PAGE_IDS.find(
    (id) => (from === "fr" || from === "en") && PAGE_SEGMENTS[id][from] === segment,
  );
  if (!page) return pathFor("home", to);
  const sub = rest.filter(Boolean).join("/");
  return `${pathFor(page, to, sub ? decodeURIComponent(sub) : undefined)}${search}`;
}
