# Architecture

A bilingual marketing site with bookings and job applications, built for mid-range Android phones on slow networks. The guiding idea: **every page is plain HTML before any JavaScript runs**, and everything the owner edits lives in one Django admin.

## Components

```
apps/web (React 19, Vite)              packages/api-client               apps/api (Django 5.2, DRF)
┌──────────────────────────┐   typed   ┌─────────────────────┐   OpenAPI  ┌──────────────────────────────┐
│ pages, layout, forms     │──calls──▶ │ openapi-fetch +      │◀─schema── │ catalog  bookings  careers    │
│ TanStack Query cache     │           │ generated types      │           │ gallery  contact   core       │
│ react-i18next (fr, en)   │           └─────────────────────┘           │ admin · cache · throttles     │
│ prerender/ (build job)   │                                              └───────┬──────────┬────────────┘
└──────────────────────────┘                                                      │          │
                                                                          PostgreSQL 16   Redis 7
```

| Path | Responsibility |
|---|---|
| `apps/api` | Data model, validation, admin, REST API under `/api/v1/`, emails, image processing |
| `packages/api-client` | `openapi.yaml` exported from Django, TypeScript types generated from it, a small typed client with `ApiError` |
| `apps/web` | The public site: routes, pages, components, translations, the pre-renderer |
| `infra` | Dockerfiles, development and production Compose files, nginx, operations scripts, CI helpers |
| `docs` | This file, decisions (ADRs), assumptions, owner guide, deployment, API reference |

## How a page reaches a phone

1. **Build and pre-render** (`pnpm build`, then the `prerender` job hourly in production). The pre-renderer asks React Router which routes each URL matches. It awaits the queries those routes declare (`handle.prefetch`) against the live API, renders to HTML, and writes `fr/a-propos.html` with its `<head>` (title, description, canonical, hreflang, Open Graph), LocalBusiness JSON-LD and the query cache as inert JSON ([ADR-013](decisions.md#adr-013--own-pre-renderer-instead-of-a-vite-ssg-plugin), [ADR-017](decisions.md#adr-017--no-inline-executable-scripts), [ADR-022](decisions.md#adr-022--pre-rendered-pages-written-as-pagehtml)).
2. **Request.** nginx returns that file: about 9 KB of compressed HTML, 9 KB of CSS and two preloaded fonts. The text is readable at once, even before the JavaScript arrives (LCP 0.8 s in mobile Lighthouse).
3. **Hydration.** The main bundle loads the lazy page module for the URL, hydrates the React tree from the embedded data without re-rendering it, then quietly refetches that data. Prices are therefore at most one page view old.
4. **Navigation.** Later pages render on the client from cached queries, with skeletons only for data not yet loaded. Code is split per page; the form libraries load only on the three form pages.

## Booking flow

```
form (React Hook Form + Zod, fr/en messages)
  └─▶ POST /api/v1/bookings/?lang=fr        throttle 10/h per IP, honeypot `website`
        validates service, date within horizon, slot in available_slots()
        stores BookingRequest(status=new, snapshots: service_name, price, duration)
  ◀── {reference, whatsapp_url}             wa.me link with the prefilled request, built server side
confirmation screen ─▶ WhatsApp (phones: automatic; computers: button + QR code)
owner confirms on WhatsApp ─▶ updates the status in the admin
```

The model is ready for real availability and payments ([ADR-008](decisions.md#adr-008--bookings-are-requests-in-v1-not-reservations)).

## Caching

| Layer | What | Lifetime | Invalidation |
|---|---|---|---|
| Browser, HTML | pre-rendered pages | 5 min, stale-while-revalidate 1 day | new deploy or hourly re-render |
| Browser, `/assets/` | hashed JS, CSS, fonts | 1 year, immutable | new hash on change |
| TanStack Query | API data in memory | 5 min stale time | refetch after hydration |
| nginx | public API GETs | per Django `Cache-Control` | short (seconds to minutes) |
| Redis | serialized API responses | 1 hour | global content version bumped on every admin save ([ADR-006](decisions.md#adr-006--global-content-version-cache-invalidation)) |

## Languages

- **Interface text:** `apps/web/src/i18n/fr.ts` (source) and `en.ts`. The English file is type-checked against the French one, so a missing key fails the build.
- **Content:** `_fr` and `_en` columns (django-modeltranslation), edited side by side in the admin. Missing English falls back to French.
- **URLs:** `/fr/...` and `/en/...` with localized segments ([ADR-015](decisions.md#adr-015--localised-urls)). The language toggle keeps the page, services tab and query string.
- **API messages:** `?lang=en` selects English validation errors from `apps/api/locale/en/` ([ADR-023](decisions.md#adr-023--english-api-messages-for-visitors-only)).

## Security

- HTTPS only (HSTS preload), secure cookies, CSRF for the admin, CORS closed (same origin).
- Strict CSP on the site: `script-src 'self'`, no inline code, maps limited to their iframe ([ADR-017](decisions.md#adr-017--no-inline-executable-scripts)).
- Write endpoints: per-endpoint throttles, honeypot field, server-side validation of every field ([ADR-009](decisions.md#adr-009--honeypot--scoped-throttles-instead-of-captcha)).
- Uploads checked by extension and file signature, with size limits ([ADR-010](decisions.md#adr-010--file-type-detection-by-signature-not-by-mime-header)). Application documents sit in private storage, downloadable only by staff ([ADR-005](decisions.md#adr-005--application-documents-in-a-separate-private-storage)).
- CI runs `pip-audit` and `pnpm audit` on every push.

## Quality gates (CI)

| Job | Checks |
|---|---|
| API | Ruff, Black, mypy `--strict`, migrations up to date, `check --deploy` with production settings, pytest on PostgreSQL (≥ 90% coverage), OpenAPI schema unchanged |
| Web | Generated types match the schema, `tsc` strict, ESLint (with a11y rules), Prettier, Vitest, production build |
| Audit | pip-audit, pnpm audit (high and above) |
| Lighthouse | Real API with seed data, pre-rendered build, mobile scores ≥ 90 in all four categories on every page |
| Docker | Production images for the API and the pre-renderer build |
