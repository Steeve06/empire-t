# Empire T Barbershop & Beauty

Website and back office for Empire T, Nkolmesseng, Yaoundé. *Plus qu'une coupe, une expérience.*

| Path | What |
|---|---|
| `apps/api` | Django 5.2 + DRF API, admin, PostgreSQL, Redis cache |
| `apps/web` | React 19 + Vite site, pre-rendered per page, French and English |
| `packages/api-client` | OpenAPI schema (`openapi.yaml`) and generated TypeScript client |
| `infra` | Dockerfiles, docker-compose, nginx |
| `docs` | Decisions, assumptions, guides |

## Run it locally

Requirements: Docker with Compose v2.

```bash
make dev        # creates .env from .env.example, then starts db, redis, api and web
```

On first boot the api container migrates, loads the seed (services, prices, openings, site settings) and creates the admin account from `DJANGO_SUPERUSER_*` in `.env`.

- Website: http://localhost:5173/fr/ (English: /en/)
- API: http://localhost:8000/api/v1/
- API reference (Swagger): http://localhost:8000/api/v1/docs/
- Admin: http://localhost:8000/admin/

## Everyday commands

```bash
make test       # backend tests with coverage, then frontend tests
make install    # once: frontend dependencies on the host (Node 22, pnpm via corepack)
make prerender  # production build of the site, rendered from the running API
make lint       # ruff, black --check, mypy --strict
make migrate    # apply migrations
make seed       # load missing seed rows (never overwrites admin edits)
make superuser  # create the admin account from .env
make schema     # export packages/api-client/openapi.yaml
```

### Without Docker (backend only)

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -r apps/api/requirements/dev.txt
cp .env.example .env   # point DATABASE_URL / REDIS_URL at localhost
cd apps/api && python manage.py migrate && python manage.py seed && python manage.py runserver
pytest                 # needs a reachable PostgreSQL (DATABASE_URL)
```

## API at a glance (`/api/v1/`)

| Method | Path | Notes |
|---|---|---|
| GET | `site/` | Shop details, hours, social links, images, recruitment status |
| GET | `categories/`, `categories/{slug}/` | Full price menu, services nested, starting price |
| GET | `services/?category=&popular=` | Paginated |
| GET | `supplements/`, `testimonials/`, `team/` | |
| GET | `gallery/?category=&featured=` | Paginated, responsive images |
| GET | `careers/openings/` | Empty after the recruitment deadline |
| GET | `bookings/slots/?date=&service=` | Bookable start times |
| POST | `bookings/` | Returns `reference` and a prefilled `whatsapp_url` |
| POST | `careers/applications/` | multipart, one or more `files` |
| POST | `contact/` | |
| GET | `health/` | Liveness/readiness |

Add `?lang=en` (or send `Accept-Language: en`) for English content. Reads are cached; writes are throttled and protected by a honeypot field.

See `docs/decisions.md` for the reasoning behind the architecture and `docs/assumptions.md` for what was assumed.
