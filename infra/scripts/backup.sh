#!/usr/bin/env bash
# Daily backup of the database and uploaded files (photos, application documents).
# Run from the repository root, by hand (`make prod-backup`) or from cron:
#   15 3 * * * cd /srv/empire-t && infra/scripts/backup.sh >> /var/log/empire-backup.log 2>&1
#
# Writes backups/db-YYYYmmdd-HHMM.dump and backups/media-YYYYmmdd-HHMM.tar.gz, keeps
# the last $BACKUP_KEEP_DAYS days (default 14), and copies them off the server with
# rclone when BACKUP_RCLONE_REMOTE is set (for example "b2:empire-t-backups").
set -euo pipefail

ENV_FILE=.env.production
COMPOSE=(docker compose --env-file "$ENV_FILE" -f infra/docker-compose.prod.yml)
# shellcheck source=infra/scripts/lib-env.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib-env.sh"
load_env "$ENV_FILE"

DEST=${BACKUP_DIR:-backups}
KEEP_DAYS=${BACKUP_KEEP_DAYS:-14}
STAMP=$(date +%Y%m%d-%H%M)
mkdir -p "$DEST"

echo "$(date -Is) database"
"${COMPOSE[@]}" exec -T db pg_dump -U "${POSTGRES_USER:-empire}" -d "${POSTGRES_DB:-empire}" \
  --format=custom --no-owner > "$DEST/db-$STAMP.dump.partial"
mv "$DEST/db-$STAMP.dump.partial" "$DEST/db-$STAMP.dump"

echo "$(date -Is) media"
"${COMPOSE[@]}" exec -T api tar -czf - -C /app media private_media > "$DEST/media-$STAMP.tar.gz.partial"
mv "$DEST/media-$STAMP.tar.gz.partial" "$DEST/media-$STAMP.tar.gz"

find "$DEST" -name 'db-*.dump' -mtime +"$KEEP_DAYS" -delete
find "$DEST" -name 'media-*.tar.gz' -mtime +"$KEEP_DAYS" -delete

if [[ -n ${BACKUP_RCLONE_REMOTE:-} ]]; then
  echo "$(date -Is) off-site copy to $BACKUP_RCLONE_REMOTE"
  rclone copy "$DEST" "$BACKUP_RCLONE_REMOTE" --include 'db-*.dump' --include 'media-*.tar.gz'
fi
echo "$(date -Is) done: $(du -sh "$DEST/db-$STAMP.dump" "$DEST/media-$STAMP.tar.gz" | tr '\n' ' ')"
