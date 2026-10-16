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
