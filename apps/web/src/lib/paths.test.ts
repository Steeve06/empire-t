import { describe, expect, it } from "vitest";

import { bookingPath, pathFor, servicesPath, translatePath } from "./paths";

describe("pathFor", () => {
  it("builds localised URLs", () => {
    expect(pathFor("home", "fr")).toBe("/fr/");
    expect(pathFor("about", "fr")).toBe("/fr/a-propos");
    expect(pathFor("about", "en")).toBe("/en/about");
    expect(servicesPath("en", "beauty")).toBe("/en/services/beauty");
  });
});

describe("bookingPath", () => {
  it("carries only the values that were filled in", () => {
    expect(bookingPath("fr", { service: "skin-fade", date: "", phone: "653147512" })).toBe(
      "/fr/reserver?service=skin-fade&phone=653147512",
    );
    expect(bookingPath("en")).toBe("/en/book");
  });
});

describe("translatePath", () => {
  it("maps a page to its translation, keeping tab and query", () => {
    expect(translatePath("/fr/reserver", "?service=barbe", "en")).toBe("/en/book?service=barbe");
    expect(translatePath("/en/services/women", "", "fr")).toBe("/fr/services/women");
    expect(translatePath("/en/", "", "fr")).toBe("/fr/");
  });

  it("falls back to the home page for unknown URLs", () => {
    expect(translatePath("/fr/nimporte-quoi", "", "en")).toBe("/en/");
    expect(translatePath("/", "", "en")).toBe("/en/");
  });
});
