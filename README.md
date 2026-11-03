# Empire T Barbershop & Beauty

Website and back office for Empire T, a barbershop, hair and beauty salon in Nkolmesseng, Yaoundé. *Plus qu'une coupe, une expérience.*

- Bilingual site (French by default, English at `/en/`), pre-rendered page by page, built for mid-range Android phones on slow networks: mobile Lighthouse 98 to 100 in every category.
- Bookings handed off to WhatsApp, with a QR code on computers; job applications with document uploads; a contact form.
- One Django admin where the owner manages prices, services, photos, openings, bookings, applications and messages.

| Path | What |
|---|---|
| `apps/api` | Django 5.2 + Django REST Framework, PostgreSQL, Redis cache, admin |
| `apps/web` | React 19 + Vite + TypeScript, Tailwind CSS 4, TanStack Query, react-i18next, React Hook Form + Zod, pre-renderer |
| `packages/api-client` | OpenAPI schema and the TypeScript client generated from it |
| `infra` | Dockerfiles, Compose (development, production), nginx, backup and HTTPS scripts, CI helpers |
| `docs` | Architecture, decisions, assumptions, guides |

## Run it locally

Requirements: Docker with Compose v2.

```bash
make dev
```

On the first start this creates `.env` from `.env.example`, starts PostgreSQL, Redis, the API and the site, applies migrations, loads the seed content (every service and price, the four openings, the site settings) and creates the admin account from `DJANGO_SUPERUSER_*`.

| | |
|---|---|
| Website | <http://localhost:5173/fr/> (English: `/en/`) |
| Admin | <http://localhost:8000/admin/> (default login `admin` / `change-me-locally`) |
| API reference | <http://localhost:8000/api/v1/docs/> |

The site's dev server proxies `/api`, `/admin` and `/media` to Django, so the browser sees a single origin, as in production.

### Without Docker

```bash
python3.12 -m venv .venv && . .venv/bin/activate && pip install -r apps/api/requirements/dev.txt
cp .env.example .env            # point DATABASE_URL and REDIS_URL at localhost
cd apps/api && python manage.py migrate && python manage.py seed && python manage.py runserver
# second terminal, Node 22:
corepack enable && pnpm install && pnpm dev
```

## Commands

```bash
make test         # backend tests (PostgreSQL, coverage ≥ 90%), then frontend and client tests
make lint         # Ruff, Black, mypy --strict · ESLint, Prettier, tsc
make migrate      # apply migrations
make seed         # add missing seed rows (never overwrites admin edits)
make superuser    # create the admin account from .env
make api-client   # export the OpenAPI schema and regenerate the TypeScript types
make prerender    # production build of the site, rendered from the running API
make messages     # compile the English API messages after editing the .po file
make help         # everything else, including the prod-* commands
```

Install the git hooks once with `pip install pre-commit && pre-commit install`.

## Quality

| | |
|---|---|
| Backend | 187 tests on PostgreSQL, 99% coverage, mypy `--strict`, Django deploy check clean |
| Frontend | 57 tests (pages, forms, routing, formatting, API client), TypeScript strict, ESLint with accessibility rules |
| Browser | Every page checked at 360 px and desktop, light and dark, French and English: no overflow, no console or hydration errors, no CSP violations |
| Lighthouse (mobile) | Performance 98 to 100, Accessibility 100, Best Practices 100, SEO 100, CLS 0 on all public pages; CI fails below 90 |

## Documentation

| | |
|---|---|
| [Owner guide](docs/owner-guide.md) (French) | Editing prices, services, photos, bookings, applications, settings |
| [Deployment guide](docs/deployment.md) | VPS setup, environment variables, HTTPS, updates, backups, monitoring |
| [Oracle Cloud (free)](docs/deploy-oracle.md) | Step by step on Oracle's Always Free ARM server, one-command install |
| [Architecture](docs/architecture.md) | Components, page delivery, caching, languages, security |
| [API reference](docs/api.md) | Conventions, endpoints, examples |
| [Decisions](docs/decisions.md) | Why each significant choice was made (ADR-001 to ADR-023) |
| [Assumptions](docs/assumptions.md) | What was decided where the brief was silent, and where to change it |

## Before launch

- The real shop email in Admin › Paramètres du site (assumption A1).
- The exact map pin (A2).
- The logo files and photos: the site uses a typographic wordmark and labelled placeholders until then (A17).
- Real testimonials and team members, if wanted: those sections stay hidden while empty (A7).
