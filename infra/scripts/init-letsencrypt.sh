#!/usr/bin/env bash
# First HTTPS certificate for a new server. Run once from the repository root:
#   infra/scripts/init-letsencrypt.sh
# nginx cannot start without a certificate, and Let's Encrypt needs nginx running to
# verify the domain. So: create a temporary self-signed certificate, start nginx, then
# replace it with a real one. The certbot service renews it automatically afterwards.
set -euo pipefail

ENV_FILE=.env.production
COMPOSE=(docker compose --env-file "$ENV_FILE" -f infra/docker-compose.prod.yml)

[[ -f $ENV_FILE ]] || { echo "Missing $ENV_FILE (copy .env.production.example)"; exit 1; }
# shellcheck source=infra/scripts/lib-env.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib-env.sh"
load_env "$ENV_FILE"
: "${DOMAIN:?DOMAIN must be set in $ENV_FILE}"
: "${LETSENCRYPT_EMAIL:?LETSENCRYPT_EMAIL must be set in $ENV_FILE}"
STAGING=()
[[ ${LETSENCRYPT_STAGING:-false} == true ]] && STAGING=(--staging)
LIVE=/etc/letsencrypt/live/$DOMAIN

echo "==> Temporary certificate for $DOMAIN"
"${COMPOSE[@]}" run --rm --entrypoint sh certbot -c "
  mkdir -p $LIVE &&
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 -subj /CN=localhost \
    -keyout $LIVE/privkey.pem -out $LIVE/fullchain.pem"

echo "==> Starting the stack"
"${COMPOSE[@]}" up -d --build

echo "==> Requesting the Let's Encrypt certificate"
"${COMPOSE[@]}" run --rm --entrypoint sh certbot -c "
  rm -rf /etc/letsencrypt/live/$DOMAIN /etc/letsencrypt/archive/$DOMAIN /etc/letsencrypt/renewal/$DOMAIN.conf"
"${COMPOSE[@]}" run --rm --entrypoint certbot certbot certonly --webroot -w /var/www/certbot \
  "${STAGING[@]}" --email "$LETSENCRYPT_EMAIL" --agree-tos --no-eff-email --non-interactive \
  -d "$DOMAIN" -d "www.$DOMAIN"

echo "==> Reloading nginx"
"${COMPOSE[@]}" exec nginx nginx -s reload
echo "Done: https://$DOMAIN"
