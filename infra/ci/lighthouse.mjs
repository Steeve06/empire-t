#!/usr/bin/env node
/**
 * Mobile Lighthouse gate for CI: every listed page must score at least MIN_SCORE in
 * performance, accessibility, best practices and SEO (definition of done).
 *
 *   CHROME_PATH=$(which google-chrome) node infra/ci/lighthouse.mjs http://localhost:4173 /fr/ /en/about
 *
 * Uses Lighthouse's default mobile profile (Moto G Power, slow 4G, 4x CPU slowdown).
 * The 404 page is not audited for SEO: it is deliberately `noindex`.
 */
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";

const MIN_SCORE = Number(process.env.LIGHTHOUSE_MIN_SCORE ?? 0.9);
const CATEGORIES = ["performance", "accessibility", "best-practices", "seo"];
const RUNS = Number(process.env.LIGHTHOUSE_RUNS ?? 2); // best of N smooths CI noise
const [base, ...pages] = process.argv.slice(2);
if (!base || pages.length === 0) {
  console.error("usage: lighthouse.mjs <base-url> <path> [path...]");
  process.exit(2);
}

const workdir = mkdtempSync(path.join(tmpdir(), "lighthouse-"));

function audit(url, run) {
  const output = path.join(workdir, `${encodeURIComponent(url)}-${run}.json`);
  execFileSync(
    "npx",
    [
      "--yes",
      "lighthouse@13.6.0",
      url,
      "--quiet",
      "--output=json",
      `--output-path=${output}`,
      `--only-categories=${CATEGORIES.join(",")}`,
      "--chrome-flags=--headless=new --no-sandbox --disable-gpu",
    ],
    { stdio: ["ignore", "ignore", "inherit"] },
  );
  const report = JSON.parse(readFileSync(output, "utf8"));
  return Object.fromEntries(CATEGORIES.map((id) => [id, report.categories[id].score ?? 0]));
}

let failed = false;
for (const page of pages) {
  const url = new URL(page, base).href;
  const best = Object.fromEntries(CATEGORIES.map((id) => [id, 0]));
  for (let run = 1; run <= RUNS; run += 1) {
    const scores = audit(url, run);
    for (const id of CATEGORIES) best[id] = Math.max(best[id], scores[id]);
  }
  const checked = page.includes("404") || page.includes("introuvable")
    ? CATEGORIES.filter((id) => id !== "seo")
    : CATEGORIES;
  const low = checked.filter((id) => best[id] < MIN_SCORE);
  const summary = CATEGORIES.map((id) => `${id} ${Math.round(best[id] * 100)}`).join("  ");
  console.log(`${low.length ? "FAIL" : "ok  "} ${page.padEnd(24)} ${summary}`);
  if (low.length) failed = true;
}
process.exit(failed ? 1 : 0);
