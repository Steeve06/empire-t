#!/bin/sh
# Run by the nginx image's entrypoint before nginx starts (files in /docker-entrypoint.d/).
# Reloads nginx every 12 hours so certificates renewed by the certbot service are served.
# Kept here rather than in `command:` because overriding the command skips the template
# rendering that the image only performs when the command is `nginx`.
set -eu
(
  while :; do
    sleep 43200
    nginx -s reload
  done
) &
