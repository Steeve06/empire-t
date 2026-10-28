import { createContext, useContext, useEffect } from "react";
import { useLocation } from "react-router";

import type { Lang } from "@empire-t/api-client";

import { LANGS, LOCALES } from "../i18n";
import { useLang, useT } from "./lang";
import { translatePath } from "./paths";

export const SITE_URL = (import.meta.env.VITE_SITE_URL ?? "http://localhost:5173").replace(
  /\/$/,
  "",
);
const DEFAULT_IMAGE = "/og-default.jpg";

export interface SeoInput {
  /** Page title, without the site name. Omit on the home page. */
  title?: string | undefined;
  description?: string | undefined;
  /** Absolute or root-relative image for social previews. */
  image?: string | null | undefined;
  noindex?: boolean;
}

export interface HeadData {
  lang: Lang;
  title: string;
  description: string;
  canonical: string;
  alternates: { hreflang: string; href: string }[];
  image: string;
  ogLocale: string;
  siteName: string;
  noindex: boolean;
}

/**
 * During pre-rendering each page writes its head here; the renderer turns it
 * into HTML. In the browser the same data updates `document.head` on navigation.
 */
export class HeadCollector {
  head: HeadData | null = null;
  readonly jsonLd: Record<string, unknown>[] = [];

  setHead(head: HeadData): void {
    this.head = head;
  }

  addJsonLd(data: Record<string, unknown>): void {
    this.jsonLd.push(data);
  }
}

export const HeadContext = createContext<HeadCollector | null>(null);

const absolute = (path: string) => (/^https?:\/\//.test(path) ? path : `${SITE_URL}${path}`);

export function buildHead(
  input: SeoInput,
  lang: Lang,
  pathname: string,
  siteName: string,
  fallbackDescription: string,
): HeadData {
  const alternates: HeadData["alternates"] = LANGS.map((code) => ({
    hreflang: code,
    href: absolute(translatePath(pathname, "", code)),
  }));
  alternates.push({ hreflang: "x-default", href: absolute(translatePath(pathname, "", "fr")) });
  return {
    lang,
    title: input.title ? `${input.title} | ${siteName}` : siteName,
    description: input.description ?? fallbackDescription,
    canonical: absolute(pathname),
    alternates,
    image: absolute(input.image ?? DEFAULT_IMAGE),
    ogLocale: LOCALES[lang].replace("-", "_"),
    siteName,
    noindex: input.noindex ?? false,
  };
}

/** Sets the page's title, description, canonical URL, hreflang and Open Graph tags. */
export function useSeo(input: SeoInput): void {
  const collector = useContext(HeadContext);
  const lang = useLang();
  const t = useT();
  const { pathname } = useLocation();
  const head = buildHead(input, lang, pathname, t("meta.siteName"), t("meta.defaultDescription"));
  collector?.setHead(head);

  const key = JSON.stringify(head);
  useEffect(() => {
    applyHead(JSON.parse(key) as HeadData);
  }, [key]);
}

/** Structured data rendered into the pre-rendered page only (crawlers read the HTML). */
export function useJsonLd(data: Record<string, unknown> | null): void {
  const collector = useContext(HeadContext);
  if (data) collector?.addJsonLd(data);
}

type Tag = ["meta" | "link", Record<string, string>];

function headTags(head: HeadData): Tag[] {
  const tags: Tag[] = [
    ["meta", { name: "description", content: head.description }],
    ["link", { rel: "canonical", href: head.canonical }],
    ...head.alternates.map((alt): Tag => [
      "link",
      { rel: "alternate", hreflang: alt.hreflang, href: alt.href },
    ]),
    ["meta", { property: "og:type", content: "website" }],
    ["meta", { property: "og:site_name", content: head.siteName }],
    ["meta", { property: "og:title", content: head.title }],
    ["meta", { property: "og:description", content: head.description }],
    ["meta", { property: "og:url", content: head.canonical }],
    ["meta", { property: "og:image", content: head.image }],
    ["meta", { property: "og:locale", content: head.ogLocale }],
    ["meta", { name: "twitter:card", content: "summary_large_image" }],
  ];
  if (head.noindex) tags.push(["meta", { name: "robots", content: "noindex" }]);
  return tags;
}

const escapeHtml = (value: string) =>
  value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/** `<script>`-safe JSON: no `</script>` or HTML comment can be closed from inside. */
export const safeJson = (data: unknown) =>
  JSON.stringify(data).replace(/</g, "\\u003c").replace(/>/g, "\\u003e").replace(/&/g, "\\u0026");

export function renderHeadHtml(head: HeadData, jsonLd: Record<string, unknown>[]): string {
  const tags = headTags(head).map(([name, attrs]) => {
    const rendered = Object.entries(attrs)
      .map(([key, value]) => `${key}="${escapeHtml(value)}"`)
      .join(" ");
    return `<${name} ${rendered} data-head>`;
  });
  const scripts = jsonLd.map(
    (data) => `<script type="application/ld+json">${safeJson(data)}</script>`,
  );
  return [`<title>${escapeHtml(head.title)}</title>`, ...tags, ...scripts].join("\n    ");
}

function applyHead(head: HeadData): void {
  document.title = head.title;
  document.documentElement.lang = head.lang;
  for (const node of document.head.querySelectorAll("[data-head]")) node.remove();
  const fragment = document.createDocumentFragment();
  for (const [name, attrs] of headTags(head)) {
    const element = document.createElement(name);
    for (const [key, value] of Object.entries(attrs)) element.setAttribute(key, value);
    element.setAttribute("data-head", "");
    fragment.append(element);
  }
  document.head.append(fragment);
}
