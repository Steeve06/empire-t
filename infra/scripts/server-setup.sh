#!/usr/bin/env bash
# One-command production install on a fresh Ubuntu 22.04/24.04 server (Oracle Cloud,
# Hetzner, DigitalOcean...). Run as root or with sudo:
#
#   curl -fsSL https://raw.githubusercontent.com/Steeve06/empire-t/main/infra/scripts/server-setup.sh \
#     | sudo bash -s -- --email you@example.com [--domain empire-t.cm]
#
# Without --domain the site gets a free address from the server's public IP:
# 203.0.113.10 -> https://203-0-113-10.sslip.io (switch to a real domain later).
#
# What it does: installs Docker, git and make; opens ports 80 and 443 in the server's
# own firewall (Oracle images block them); adds swap on small servers; clones the
# repository to /srv/empire-t; writes .env.production with freshly generated secrets;
# then gets the HTTPS certificate, starts the stack, loads the content and renders
# the pages. Safe to re-run: existing secrets and data are kept.
set -euo pipefail

REPO_URL=${REPO_URL:-https://github.com/Steeve06/empire-t.git}
APP_DIR=${APP_DIR:-/srv/empire-t}
EMAIL=""
DOMAIN=""

usage() { echo "usage: server-setup.sh --email you@example.com [--domain example.com]"; exit 2; }
log() { printf '\n\033[1;33m==> %s\033[0m\n' "$*"; }

# The account that owns the app: the one that called sudo (ubuntu on Oracle), else root.
OWNER=${SUDO_USER:-root}

random_secret() { openssl rand -base64 48 | tr -dc 'A-Za-z0-9' | head -c "$1"; }

# Replace KEY=... in the env file, or append it.
set_env() {
  local key=$1 value=$2 file=$3
  if grep -q "^${key}=" "$file"; then
    sed -i "s|^${key}=.*|${key}=${value//|/\\|}|" "$file"
  else
    printf '%s=%s\n' "$key" "$value" >> "$file"
  fi
}

# Keep a value already present (re-runs must not rotate the database password).
current_env() { grep -E "^$1=" "$2" | head -1 | cut -d= -f2- || true; }

write_env() {
  local file=$1 domain=$2 email=$3
  [[ -f $file ]] || cp "$APP_DIR/.env.production.example" "$file"
  chmod 600 "$file"
  local db_password secret admin_password
  db_password=$(current_env POSTGRES_PASSWORD "$file"); db_password=${db_password:-$(random_secret 40)}
  secret=$(current_env DJANGO_SECRET_KEY "$file"); secret=${secret:-$(random_secret 64)}
  admin_password=$(current_env DJANGO_SUPERUSER_PASSWORD "$file"); admin_password=${admin_password:-$(random_secret 20)}
  set_env DOMAIN "$domain" "$file"
  set_env LETSENCRYPT_EMAIL "$email" "$file"
  set_env POSTGRES_PASSWORD "$db_password" "$file"
  set_env DJANGO_SECRET_KEY "$secret" "$file"
  set_env DJANGO_ALLOWED_HOSTS "$domain,www.$domain,api,127.0.0.1" "$file"
  set_env CSRF_TRUSTED_ORIGINS "https://$domain,https://www.$domain" "$file"
  set_env ADMIN_URL_BASE "https://$domain" "$file"
  set_env DJANGO_SUPERUSER_EMAIL "$email" "$file"
  set_env DJANGO_SUPERUSER_PASSWORD "$admin_password" "$file"
}

open_firewall() {
  # Oracle's Ubuntu images ship iptables rules that reject everything except SSH.
  # Insert the web ports before the REJECT line of the saved rules and reload them
  # (before Docker starts, so Docker's own rules are added on top afterwards).
  local rules=/etc/iptables/rules.v4
  if [[ -f $rules ]] && ! grep -q -- '--dport 80 ' "$rules"; then
    sed -i '/-A INPUT -j REJECT/i -A INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT\n-A INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT' "$rules"
    iptables-restore < "$rules"
    echo "Opened ports 80 and 443 in $rules"
  fi
  # ufw is inactive on Oracle images; on other providers allow the ports if it is on.
  if command -v ufw > /dev/null && ufw status | grep -q "Status: active"; then
    ufw allow 80/tcp && ufw allow 443/tcp
  fi
}

add_swap_if_small() {
  local mem_kb
  mem_kb=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
  if (( mem_kb < 3 * 1024 * 1024 )) && ! swapon --show | grep -q .; then
    fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile > /dev/null && swapon /swapfile
    grep -q '^/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "Added 2 GB of swap (the server has less than 3 GB of memory)"
  fi
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case $1 in
      --email) EMAIL=${2:-}; shift 2 ;;
      --domain) DOMAIN=${2:-}; shift 2 ;;
      -h | --help) usage ;;
      *) echo "Unknown option: $1"; usage ;;
    esac
  done
  [[ -n $EMAIL ]] || usage
  [[ $EUID -eq 0 ]] || { echo "Run as root (sudo)."; exit 1; }
}

main() {
  parse_args "$@"

  log "System packages"
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -q
  apt-get upgrade -yq
  apt-get install -yq git make curl openssl

  log "Firewall and memory"
  open_firewall
  add_swap_if_small

  log "Docker"
  if ! command -v docker > /dev/null; then
    curl -fsSL https://get.docker.com | sh
  fi
  if [[ $OWNER != root ]]; then usermod -aG docker "$OWNER"; fi

  log "Code in $APP_DIR"
  if [[ -d $APP_DIR/.git ]]; then
    # As the owner: git refuses to operate on a repository owned by another user
    sudo -u "$(stat -c %U "$APP_DIR")" git -C "$APP_DIR" pull --ff-only
  else
    git clone "$REPO_URL" "$APP_DIR"
  fi

  if [[ -z $DOMAIN ]]; then
    local ip
    ip=$(curl -fsS https://api.ipify.org)
    DOMAIN="${ip//./-}.sslip.io"
    echo "No --domain given: using $DOMAIN"
  fi

  log "Configuration (.env.production)"
  write_env "$APP_DIR/.env.production" "$DOMAIN" "$EMAIL"
  chown -R "$OWNER:$OWNER" "$APP_DIR"

  log "HTTPS certificate and first start (the first build takes 5 to 15 minutes)"
  cd "$APP_DIR"
  infra/scripts/init-letsencrypt.sh

  log "Content and pages"
  make prod-bootstrap
  make prod-refresh

  local admin_password
  admin_password=$(current_env DJANGO_SUPERUSER_PASSWORD .env.production)
  cat << EOF

$(printf '\033[1;32m')Empire T is online.$(printf '\033[0m')

  Site:   https://$DOMAIN/fr/
  Admin:  https://$DOMAIN/admin/
          user: admin   password: $admin_password
          (change it after logging in; it is also in $APP_DIR/.env.production)

Next: schedule the nightly backup (docs/deployment.md, section 6).
EOF
}

# Allow tests to source the helpers without running the installation.
if [[ ${BASH_SOURCE[0]:-$0} == "$0" ]]; then
  main "$@"
fi
