# Deployment guide

Production runs as one Docker Compose stack on a small Linux server (assumption A13): nginx with Let's Encrypt HTTPS, Django under gunicorn, PostgreSQL 16, Redis 7, and a pre-renderer that refreshes the static pages every hour. Expect about 15 to 20 minutes for a first install.

```
            ┌────────────── server (Docker Compose, infra/docker-compose.prod.yml) ─────────────┐
 visitor ──▶│ nginx :443 ─┬─ /fr/…, /en/…  → static pages (volume `site`) ◀── prerender (hourly)│
            │             ├─ /api/, /admin/, /static/ → api (gunicorn) ──▶ db (PostgreSQL)      │
            │             └─ /media/       → photos (volume `media`)        └─▶ redis (cache)    │
            │ certbot: renews the certificate                                                    │
            └────────────────────────────────────────────────────────────────────────────────────┘
```

## 1. Server

| | Minimum | Comfortable |
|---|---|---|
| CPU / RAM | 1 vCPU, 2 GB | 2 vCPU, 4 GB |
| Disk | 25 GB SSD | 50 GB (photos and backups grow) |
| OS | Ubuntu 24.04 LTS | |

Any VPS works (Hetzner, DigitalOcean, OVHcloud, Contabo, a Cameroonian host). A European region (Paris, Frankfurt) usually gives Yaoundé the lowest latency. A managed platform (Render, Railway, Fly.io) also works: run the `api` image as a web service, a managed PostgreSQL and Redis, the `prerender` image as a scheduled job writing to object storage, and a CDN in front. This guide covers the VPS, which is cheaper and simpler.

```bash
# As root on a fresh server
apt update && apt upgrade -y
curl -fsSL https://get.docker.com | sh                 # Docker Engine + Compose plugin
adduser --disabled-password --gecos "" deploy && usermod -aG docker deploy
ufw allow OpenSSH && ufw allow 80 && ufw allow 443 && ufw --force enable
```

## 2. Domain

At your DNS provider, point both names at the server's IPv4 address:

| Type | Name | Value |
|---|---|---|
| A | `empire-t.cm` | server IP |
| A | `www` | server IP |

Wait until `dig +short empire-t.cm` returns the IP before requesting the certificate.

## 3. First install

```bash
# As the deploy user
git clone https://github.com/Steeve06/empire-t.git /srv/empire-t
cd /srv/empire-t
cp .env.production.example .env.production
chmod 600 .env.production
nano .env.production
```

Fill in at least the following (each variable is documented in the file):

| Variable | Value |
|---|---|
| `DOMAIN`, `LETSENCRYPT_EMAIL` | your domain, an email for certificate expiry notices |
| `POSTGRES_PASSWORD` | `openssl rand -base64 32` |
| `DJANGO_SECRET_KEY` | `python3 -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DJANGO_ALLOWED_HOSTS` | `yourdomain,www.yourdomain,api,127.0.0.1` (keep `api` and `127.0.0.1`: the pre-renderer and the health check use them) |
| `CSRF_TRUSTED_ORIGINS`, `ADMIN_URL_BASE` | `https://yourdomain` |
| `EMAIL_URL` | your SMTP server, e.g. `smtp+tls://user:key@smtp-relay.brevo.com:587` (Brevo's free plan covers this volume) |
| `DJANGO_SUPERUSER_*` | the first admin account |

Then start everything with HTTPS, and load the content:

```bash
make prod-https       # temporary certificate → start the stack → real Let's Encrypt certificate
make prod-bootstrap   # services, prices, openings and site settings, plus the admin account
make prod-refresh     # re-render the pages with the content just loaded
```

`make prod-https` runs `infra/scripts/init-letsencrypt.sh` once. Set `LETSENCRYPT_STAGING=true` for a first trial run to avoid Let's Encrypt's rate limits, then set it back to `false` and run it again.

### Check

```bash
curl -I https://empire-t.cm/fr/                 # 200, with strict-transport-security and content-security-policy
curl https://empire-t.cm/api/v1/health/         # {"database":"ok","cache":"ok"}
docker compose --env-file .env.production -f infra/docker-compose.prod.yml ps   # all running, api healthy
```

Then open `https://empire-t.cm/admin/`, log in, change the password, and complete the launch checklist in the [owner guide](owner-guide.md#9-paramètres-du-site): real email, exact map pin, social links.

## 4. Environment variables

`.env.production` is read by the api container and by the scripts. Beyond the required ones above:

| Variable | Default | Purpose |
|---|---|---|
| `USE_S3` and `S3_*` | `false` | Store photos and application files on S3-compatible storage (Cloudflare R2, Backblaze B2, AWS S3) instead of the server disk. Application files go to a private prefix with 5-minute signed links. |
| `GUNICORN_WORKERS` | 3 | 2 × CPU + 1, capped at 5 |
| `PRERENDER_INTERVAL_SECONDS` | 3600 | How often static pages are re-rendered from the database |
| `DJANGO_ADMINS_EMAILS` | empty | Emailed the details of every server error |
| `LOG_LEVEL` | INFO | API log level |
| `BACKUP_*` | see file | Backup directory, retention, off-site rclone remote |

## 5. Updating

```bash
cd /srv/empire-t
make prod-deploy        # git pull, rebuild images, restart changed services (migrations run on start)
```

Visitors keep being served during the rebuild; the restart takes a few seconds. Old build files stay in the `site` volume, so pages already open in a browser keep working.

**Content changes need no deploy.** Visitors' browsers fetch fresh prices on every visit. The static copies served to Google refresh within the hour, or immediately with `make prod-refresh`.

## 6. Backups

`infra/scripts/backup.sh` (`make prod-backup`) writes a PostgreSQL dump and an archive of uploaded files (photos and application documents) to `backups/`. It keeps 14 days and copies everything off the server when `BACKUP_RCLONE_REMOTE` is set.

**Schedule it** (required): `crontab -e` as the deploy user:

```cron
15 3 * * * cd /srv/empire-t && infra/scripts/backup.sh >> /srv/empire-t/backups/backup.log 2>&1
```

**Keep a copy off the server.** Install rclone (`curl https://rclone.org/install.sh | sudo bash`), run `rclone config` to add a remote (Backblaze B2 costs a few cents a month at this size), and set `BACKUP_RCLONE_REMOTE=b2:empire-t-backups`.

**Restore** (also test it once, e.g. on a staging server):

```bash
make prod-restore DB=backups/db-20261101-0315.dump MEDIA=backups/media-20261101-0315.tar.gz
```

The script asks for confirmation, stops the API, restores the database (`pg_restore --clean`) and the files, then restarts.

## 7. HTTPS

`certbot` renews certificates automatically (it checks twice a day), and nginx reloads every 12 hours to pick them up. To check: `docker compose --env-file .env.production -f infra/docker-compose.prod.yml run --rm certbot certificates`.

nginx sends HSTS (with preload), a strict Content-Security-Policy (no inline scripts on the public site), and `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` and `Cross-Origin-Opener-Policy` on every response (`infra/nginx/snippets/`). Django adds secure cookies and CSRF protection.

## 8. Monitoring and logs

- **Uptime:** point a free monitor (UptimeRobot, Better Stack) at `https://yourdomain/api/v1/health/`. It returns 503 if the database is unreachable.
- **Logs:** `make prod-logs`, or `... logs api` for one service. Logs rotate at 5 × 10 MB per service.
- **Errors:** set `DJANGO_ADMINS_EMAILS` to receive each server error by email.
- **Disk:** `df -h` and `du -sh backups`. Photos are stored as compact WebP (about 30 to 200 KB each).

## 9. Troubleshooting

| Symptom | Check |
|---|---|
| Certificate request fails | DNS points at the server (`dig +short yourdomain`), ports 80 and 443 are open, `LETSENCRYPT_STAGING=false` |
| `400 Bad Request` from the API | The host is missing from `DJANGO_ALLOWED_HOSTS` (it must include `api` and `127.0.0.1` too) |
| Pages show old prices to search engines | `make prod-refresh`; check `... logs prerender` for API errors |
| No email for applications or messages | `EMAIL_URL` is still `consolemail://`, or the SMTP credentials are wrong (`... logs api`). Submissions are always saved in the admin regardless. |
| Uploads rejected with 413 | Above the limits (15 MB per file, 40 MB per application); nginx allows 45 MB per request |
| Site down after a server reboot | `docker compose ... up -d` (services restart automatically unless stopped by hand) |
