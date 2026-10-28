# Architecture decisions

Short records of choices where a reasonable alternative existed. Newest at the bottom.

## ADR-001 · Django 5.2 LTS instead of the latest 5.x
**Choice:** Django 5.2 (LTS, security support until April 2028).
**Why:** a small business site should not need a framework upgrade every eight months. 5.2 has everything required (`STORAGES`, `CheckConstraint(condition=…)`, async-ready ORM).

## ADR-002 · One REST API, no GraphQL, no server-side rendering in Django
**Choice:** DRF JSON API consumed by a pre-rendered React site.
**Why:** the content is small and read-mostly. REST + HTTP caching + nginx edge caching is the simplest fast path. OpenAPI (drf-spectacular) gives typed contracts to the frontend through `packages/api-client`.

## ADR-003 · Translations stored as columns (django-modeltranslation)
**Choice:** `name_fr` / `name_en` columns, French fallback.
**Why:** the owner edits both languages side by side in one admin form, queries stay single-table (no joins per language), and a missing English text falls back to French instead of showing nothing. The non-tabbed admin is used because the tabbed variant loads jQuery UI from a CDN, which the production CSP blocks.

## ADR-004 · Responsive WebP variants generated on upload, not on request
**Choice:** each uploaded photo is re-encoded once into 480/960/1600 px WebP (never upscaled); metadata (`width`, `height`, `variants`) is stored in `image_meta`. The original upload is discarded.
**Why:** no image server or CDN transform to pay for, zero CPU per page view, and the API can return `srcset`, `width` and `height` so the frontend avoids layout shift. Phones in Yaoundé typically need the 480 px file (~30–60 KB) instead of a multi-megabyte camera JPEG.
**Trade-off:** changing the widths later requires a one-off reprocessing command.

## ADR-005 · Application documents in a separate private storage
**Choice:** `STORAGES["private"]`: a directory never served by nginx (dev) or a private S3 prefix with 5-minute signed URLs (prod). Staff download through an admin view that checks `view` permission.
**Why:** CVs and national ID copies are personal data. Public `/media/` URLs would be guessable and indexable.

## ADR-006 · Global content-version cache invalidation
**Choice:** every cached API response key includes a single "content version" number; saving or deleting any public content model increments it. Keys also include the local date and language. Entries expire after one hour regardless.
**Why:** content changes a few times a week. Tracking which endpoint depends on which model would be more code and more ways to serve stale prices. The cost (all read caches refill after an edit) is a few dozen cheap queries.
**Also:** Redis errors are ignored (`IGNORE_EXCEPTIONS`), so a cache outage degrades to uncached responses, never to errors.

## ADR-007 · Seed command never overwrites owner edits
**Choice:** `manage.py seed` creates missing rows only; `--force` resets to seed values.
**Why:** the dev container runs `seed` on every boot. A naive `update_or_create` would silently revert prices the owner changed in the admin.

## ADR-008 · Bookings are requests in v1, not reservations
**Choice:** the API stores a request and hands off to WhatsApp; it validates opening hours, lead time and horizon but does not check chair capacity.
**Why:** the shop takes walk-ins and confirms by WhatsApp today; enforcing capacity now would block real customers on data the owner does not maintain.
**Ready for v2 without a rewrite:** each booking snapshots `duration_minutes`, `price_snapshot` and `service_name`, exposes `starts_at`/`ends_at`, has a `status` lifecycle (only `confirmed` would block a slot) and payment fields (`payment_status`, `amount_due`, `payment_reference`) defaulting to "not required". Availability becomes a filter in `available_slots()`; Mobile Money becomes a new app writing those fields.

## ADR-009 · Honeypot + scoped throttles instead of CAPTCHA
**Choice:** a hidden `website` field on every form plus per-endpoint rate limits (bookings 10/h, applications 5/h, contact 5/h per IP).
**Why:** CAPTCHAs add ~200 KB of third-party script and frustrate users on slow networks. A small salon is a low-value spam target; these two layers stop the common bots. If abuse appears, Cloudflare Turnstile can be added behind the same serializer mixin.

## ADR-010 · File type detection by signature, not by MIME header
**Choice:** uploads are checked by extension *and* leading bytes (PDF, DOC/DOCX, JPEG, PNG, WebP, HEIC, MP4, MOV), 15 MB per file, 40 MB and 8 files per application.
**Why:** the browser-supplied `Content-Type` is attacker-controlled. HEIC and MOV are allowed because that is what iPhones produce for photos and videos of work.
**Known limit:** DOCX is a ZIP container, so any ZIP renamed `.docx` passes; files are only ever downloaded by staff, never executed or served publicly.

## ADR-011 · Explicit managers on every model
**Choice:** each model declares `objects: ClassVar[...]` (custom managers are small explicit classes, not `from_queryset`).
**Why:** modeltranslation swaps managers at runtime, which the django-stubs mypy plugin cannot follow. Explicit managers keep `mypy --strict` meaningful instead of degrading querysets to `Any`.

## ADR-012 · Plain pytest fixtures, no factory library
**Choice:** tests build data from the real seed command and small fixtures.
**Why:** the domain is small; testing against the actual seed also verifies the content the owner will see. One dependency fewer.

## ADR-013 · Own pre-renderer instead of a Vite SSG plugin
**Choice:** `apps/web/src/prerender/` renders every public URL with React Router's static handler and `renderToString`, after awaiting the queries each route declares (`handle.prefetch`). The output is plain HTML per page, with its `<head>`, LocalBusiness JSON-LD and the dehydrated TanStack Query cache. It runs as a deploy-time job against the live API, not inside `vite build`.
**Why:** SSG plugins (vite-react-ssg and similar) lag behind React Router and React releases and render at build time, when the production API is usually unreachable. About 150 lines of our own code give full control: the job fails loudly if any API call fails, so an error page is never frozen into static HTML.
**Freshness:** pre-rendered data is marked stale, so the browser silently refetches it once after hydration (prices are never more than a page view out of date for visitors). Crawlers see the snapshot, which `make prerender` (or the nightly job in the deployment guide) refreshes.

## ADR-014 · Same-origin API, storage URLs not derived from the Host header
**Choice:** the browser calls `/api/v1/` on its own origin: nginx routes it in production and the Vite dev server proxies it in development. Image URLs in API responses are storage URLs as-is (root-relative locally, absolute on S3).
**Why:** no CORS preflight on slow networks, no cookies or origins to configure, and identical cached responses for every client, including the pre-renderer, which calls the API from inside Docker. The previous `build_absolute_uri` produced `http://api:8000/media/...` links in pre-rendered pages.

## ADR-015 · Localised URLs
**Choice:** `/fr/a-propos`, `/fr/reserver`, `/en/about`, `/en/book`... Each page has one id and one segment per language (`lib/paths.ts`); the language toggle maps between them and keeps the services tab and query string.
**Why:** French URLs read naturally to the main audience and rank for French searches. hreflang links tie each pair together for Google.

## ADR-016 · A darker gold for text on light backgrounds
**Choice:** the brand gold `#B8923A` stays for buttons, borders and text on dark sections. Gold text on ivory or white (eyebrows, prices, links) uses `--c-gold-ink` `#86661F`.
**Why:** `#B8923A` on `#FAF7F2` is 2.7:1, below the 4.5:1 WCAG AA minimum the brief requires. `#86661F` is 5.0:1 on ivory and 5.3:1 on white, and still reads as the same gold. On dark backgrounds the brand gold measures 6.5:1 and is kept. The same reasoning gave the WhatsApp button `#1E7E34` (5.3:1 with white) instead of the prototype's `#25A244` (3.3:1).

## ADR-017 · No inline executable scripts
**Choice:** the hydration state is embedded as `<script type="application/json">` and parsed by the main bundle; JSON-LD is `application/ld+json`. React Router's own hydration script is disabled (`hydrate={false}`); lazy route modules for the first URL are loaded before hydrating instead.
**Why:** the production CSP can then be `script-src 'self'`, with no hashes or nonces to keep in sync with every build.

## ADR-018 · Google Maps behind a click-to-load facade
**Choice:** the map area shows the address with "Afficher la carte"; the iframe loads only when asked. An "Ouvrir dans Google Maps" link is always present.
**Why:** the embed pulls over 1 MB of script and cookies on page load, which alone would push the home page below Lighthouse 90 on a mid-range phone, and costs visitors mobile data for something most never open.

## ADR-019 · Toolchain versions held back on purpose
**Choice:** TypeScript 5.9, ESLint 10 with `eslint-plugin-jsx-a11y-x`, React Router 7.
**Why:** typescript-eslint and openapi-typescript do not yet support TypeScript 7. The original `eslint-plugin-jsx-a11y` has had no release since 2024 and stops at ESLint 9, which is end-of-life; the `-x` fork runs the same accessibility rules on ESLint 10. React Router 7 is the maintained line whose data and static-rendering APIs this project uses; moving to 8 is a separate, deliberate upgrade.

## ADR-020 · openapi-fetch as the API client
**Choice:** `packages/api-client` wraps `openapi-fetch` (about 6 KB) with the types `openapi-typescript` generates from `openapi.yaml`, plus an `ApiError` carrying DRF field errors. CI regenerates the types and fails on any difference.
**Why:** request paths, query parameters and response shapes are checked by the compiler against the backend contract, with no code generator runtime and no hand-written DTOs to drift.
