import type { Lang } from "@empire-t/api-client";
import type { TFunction } from "i18next";

import { LOCALES } from "../i18n";

type T = TFunction;

/** 3500 → "3 500" with a non-breaking thin space, the French and Cameroonian convention. */
export function formatAmount(amount: number, lang: Lang): string {
  return new Intl.NumberFormat(LOCALES[lang], { maximumFractionDigits: 0 }).format(amount);
}

export interface Priced {
  price?: number | null;
  price_is_from?: boolean;
  price_on_quote?: boolean;
}

/** "1 000 F", "dès 3 000 F" or "Sur devis". */
export function formatPrice(item: Priced, lang: Lang, t: T): string {
  if (item.price_on_quote || item.price == null) return t("price.onQuote");
  const amount = t("price.currency", { amount: formatAmount(item.price, lang) });
  return item.price_is_from ? t("price.from", { price: amount }) : amount;
}

export function formatDuration(min: number, max: number | null | undefined, t: T): string {
  return max && max !== min
    ? t("duration.range", { min, max })
    : t("duration.minutes", { count: min });
}

/** ISO date "2026-11-15" → "15 novembre 2026" / "15 November 2026", calendar-safe (no TZ shift). */
export function formatDate(iso: string, lang: Lang, options?: Intl.DateTimeFormatOptions): string {
  const [year, month, day] = iso.split("-").map(Number);
  const date = new Date(Date.UTC(year ?? 1970, (month ?? 1) - 1, day ?? 1));
  return new Intl.DateTimeFormat(LOCALES[lang], {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
    ...options,
  }).format(date);
}

/** "07:00" → "7h00" in French, "7:00" in English. */
export function formatTime(hhmm: string, lang: Lang): string {
  const [hours = "0", minutes = "00"] = hhmm.split(":");
  const h = String(Number(hours));
  return lang === "fr" ? `${h}h${minutes}` : `${h}:${minutes}`;
}

/** Today's date in Yaoundé (UTC+1, no DST), as YYYY-MM-DD, whatever the device time zone. */
export function todayInYaounde(now: Date = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Africa/Douala" }).format(now);
}
