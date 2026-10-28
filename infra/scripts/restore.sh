#!/usr/bin/env bash
# Restore a backup made by backup.sh. Replaces the current database and uploaded files.
#   infra/scripts/restore.sh backups/db-20261101-0315.dump [backups/media-20261101-0315.tar.gz]
set -euo pipefail

DB_DUMP=${1:?usage: restore.sh <db-dump> [media-archive]}
MEDIA_ARCHIVE=${2:-}
ENV_FILE=.env.production
COMPOSE=(docker compose --env-file "$ENV_FILE" -f infra/docker-compose.prod.yml)
set -a
# shellcheck disable=SC1090  # the env file path is chosen at run time
source "$ENV_FILE"
set +a

read -r -p "This replaces the live database${MEDIA_ARCHIVE:+ and media}. Type RESTORE to continue: " answer
[[ $answer == RESTORE ]] || { echo "Cancelled."; exit 1; }

echo "==> Stopping the API and the pre-renderer"
"${COMPOSE[@]}" stop api prerender

echo "==> Restoring the database from $DB_DUMP"
"${COMPOSE[@]}" exec -T db pg_restore -U "${POSTGRES_USER:-empire}" -d "${POSTGRES_DB:-empire}" \
  --clean --if-exists --no-owner --single-transaction < "$DB_DUMP"

if [[ -n $MEDIA_ARCHIVE ]]; then
  echo "==> Restoring media from $MEDIA_ARCHIVE"
  "${COMPOSE[@]}" run --rm -T --no-deps --entrypoint sh api -c \
    "rm -rf /app/media/* /app/private_media/* && tar -xzf - -C /app" < "$MEDIA_ARCHIVE"
fi

echo "==> Starting again (migrations run on start, pages re-render)"
"${COMPOSE[@]}" up -d api prerender
echo "Restore complete."
