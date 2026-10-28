import { describe, expect, it } from "vitest";

import { createI18n } from "../i18n";
import { formatDate, formatDuration, formatPrice, formatTime, todayInYaounde } from "./format";

const fr = createI18n("fr").getFixedT("fr");
const en = createI18n("en").getFixedT("en");
const NBSP = String.fromCharCode(0xa0);
const NNBSP = String.fromCharCode(0x202f);
const nbsp = (value: string) => value.replaceAll(NBSP, " ").replaceAll(NNBSP, " ");

describe("formatPrice", () => {
  it("formats fixed, starting and on-quote prices in both languages", () => {
    expect(nbsp(formatPrice({ price: 3500 }, "fr", fr))).toBe("3 500 F");
    expect(nbsp(formatPrice({ price: 3000, price_is_from: true }, "fr", fr))).toBe("dès 3 000 F");
    expect(nbsp(formatPrice({ price: 3000, price_is_from: true }, "en", en))).toBe("from 3,000 F");
    expect(formatPrice({ price: null, price_on_quote: true }, "fr", fr)).toBe("Sur devis");
    expect(formatPrice({ price: null, price_on_quote: true }, "en", en)).toBe("On quote");
  });

  it("never breaks a line between the amount and the currency", () => {
    expect(formatPrice({ price: 500 }, "fr", fr)).toBe(`500${NBSP}F`);
  });
});

describe("formatDuration", () => {
  it("shows a single value or a range", () => {
    expect(formatDuration(20, null, fr)).toBe("20 min");
    expect(formatDuration(60, 90, fr)).toBe("60 à 90 min");
    expect(formatDuration(60, 90, en)).toBe("60 to 90 min");
    expect(formatDuration(45, 45, en)).toBe("45 min");
  });
});

describe("dates and times", () => {
  it("formats an ISO date without a time-zone shift", () => {
    expect(formatDate("2026-11-15", "fr")).toBe("15 novembre 2026");
    expect(formatDate("2026-11-15", "en")).toBe("15 November 2026");
  });

  it("formats times the local way", () => {
    expect(formatTime("07:00", "fr")).toBe("7h00");
    expect(formatTime("21:30", "en")).toBe("21:30");
  });

  it("uses Yaoundé's date, not the device's", () => {
    // 23:30 UTC on 14 Nov is already 00:30 on 15 Nov in Yaoundé (UTC+1)
    expect(todayInYaounde(new Date("2026-11-14T23:30:00Z"))).toBe("2026-11-15");
  });
});
