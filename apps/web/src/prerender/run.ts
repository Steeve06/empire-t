/**
 * Build-time pre-renderer (`pnpm prerender`, after `pnpm build`).
 *
 * Fetches content from the running API, renders every public page in both
 * languages to static HTML (with its <head>, JSON-LD and the data needed to
 * hydrate), then writes sitemap.xml and robots.txt. nginx serves the result.
 *
 *   PRERENDER_API_URL  API origin to read from (default http://localhost:8000)
 *   SITE_OUTPUT_DIR    Copy the build there and render into it (the volume nginx serves);
 *                      by default pages are written into dist/ itself
 *   VITE_SITE_URL      Public origin used in canonical URLs (baked in at build)
 */
import { cp, mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

import { createApiClient, type Lang } from "@empire-t/api-client";

import { buildRoutes } from "../app/routes";
import { STATE_ELEMENT_ID } from "../app/hydration";
import { LANGS } from "../i18n";
import { pathFor, servicesPath, type PageId } from "../lib/paths";
import { renderHeadHtml, safeJson, SITE_URL } from "../lib/seo";
import { renderPage } from "./render";

const BUILD = path.resolve(import.meta.dirname, "../dist");
const DIST = process.env.SITE_OUTPUT_DIR ? path.resolve(process.env.SITE_OUTPUT_DIR) : BUILD;
const API_URL = (process.env.PRERENDER_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
const ORIGIN = "http://prerender.local";

interface Target {
  path: string;
  file: string;
  lang: Lang;
  /** Listed in sitemap.xml with its translation. */
  sitemapAlternates?: Record<Lang, string>;
}

const fileFor = (urlPath: string) => path.join(urlPath.replace(/^\//, ""), "index.html");

async function listTargets(api: ReturnType<typeof createApiClient>): Promise<Target[]> {
  const [site, categories] = await Promise.all([api.site("fr"), api.categories("fr")]);
  const pages: PageId[] = ["home"];
  const targets: Target[] = [];

  const add = (build: (lang: Lang) => string) => {
    const alternates = Object.fromEntries(LANGS.map((lang) => [lang, build(lang)])) as Record<
      Lang,
      string
    >;
    for (const lang of LANGS) {
      targets.push({
        path: alternates[lang],
        file: fileFor(alternates[lang]),
        lang,
        sitemapAlternates: alternates,
      });
    }
  };
  for (const page of pages) add((lang) => pathFor(page, lang));
  if (pages.includes("services")) {
    for (const category of categories) add((lang) => servicesPath(lang, category.slug));
  }
  if (!site.recruitment_open)
    console.info("Recruitment is closed: careers page left out of the sitemap");

  targets.push(
    { path: "/fr/page-introuvable", file: "404.html", lang: "fr" },
    { path: "/en/page-not-found", file: "en/404.html", lang: "en" },
    { path: "/fr/__500", file: "500.html", lang: "fr" },
  );
  return targets;
}

async function fontPreloads(): Promise<string> {
  const assets = await readdir(path.join(DIST, "assets"));
  const wanted = [
    /^cormorant-garamond-latin-600-normal-.*\.woff2$/,
    /^manrope-latin-wght-normal-.*\.woff2$/,
  ];
  return wanted
    .map((pattern) => assets.find((file) => pattern.test(file)))
    .filter((file): file is string => Boolean(file))
    .map(
      (file) =>
        `<link rel="preload" href="/assets/${file}" as="font" type="font/woff2" crossorigin>`,
    )
    .join("\n    ");
}

function sitemap(targets: Target[]): string {
  const today = new Date().toISOString().slice(0, 10);
  const urls = targets
    .filter((target) => target.sitemapAlternates)
    .map((target) => {
      const alternates = Object.entries(target.sitemapAlternates ?? {})
        .map(
          ([lang, href]) =>
            `<xhtml:link rel="alternate" hreflang="${lang}" href="${SITE_URL}${href}"/>`,
        )
        .join("");
      return `<url><loc>${SITE_URL}${target.path}</loc><lastmod>${today}</lastmod>${alternates}</url>`;
    });
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n${urls.join("\n")}\n</urlset>\n`;
}

const robots = () =>
  [
    "User-agent: *",
    "Allow: /",
    "Disallow: /admin/",
    "Disallow: /api/",
    `Sitemap: ${SITE_URL}/sitemap.xml`,
    "",
  ].join("\n");

async function main(): Promise<void> {
  const started = Date.now();
  if (DIST !== BUILD) await cp(BUILD, DIST, { recursive: true, force: true });
  const template = await readFile(path.join(BUILD, "index.html"), "utf8");
  const api = createApiClient({ baseUrl: API_URL });
  const routes = buildRoutes({ statusPages: true });
  const preloads = await fontPreloads();
  const targets = await listTargets(api);

  for (const target of targets) {
    const page = await renderPage(routes, api, `${ORIGIN}${target.path}`);
    const document = template
      .replace('<html lang="fr">', () => `<html lang="${target.lang}">`)
      .replace(/<title>[^<]*<\/title>\s*/, "")
      .replace("<!--app-head-->", () =>
        [preloads, renderHeadHtml(page.head, page.jsonLd)].join("\n    "),
      )
      .replace("<!--app-html-->", () => page.html)
      .replace(
        "<!--app-state-->",
        () =>
          `<script type="application/json" id="${STATE_ELEMENT_ID}">${safeJson(page.state)}</script>`,
      );
    const output = path.join(DIST, target.file);
    await mkdir(path.dirname(output), { recursive: true });
    await writeFile(output, document);
    console.info(`  ${target.path} → ${target.file}`);
  }

  await writeFile(path.join(DIST, "sitemap.xml"), sitemap(targets));
  await writeFile(path.join(DIST, "robots.txt"), robots());
  console.info(
    `Pre-rendered ${targets.length} pages from ${API_URL} in ${Date.now() - started} ms`,
  );
}

main().then(
  () => process.exit(0),
  (error: unknown) => {
    console.error("Pre-rendering failed:", error instanceof Error ? error.message : error);
    process.exit(1);
  },
);
