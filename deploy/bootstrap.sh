#!/usr/bin/env bash
# =====================================================================
# Barormebel — serverni BIR MARTA tayyorlash skripti (Ubuntu 22.04/24.04)
# root sifatida ishga tushiring:
#   sudo bash bootstrap.sh
# DNS: barormebel.uz va www.barormebel.uz -> server IP ni ko'rsatishi SHART.
# =====================================================================
set -euo pipefail

DOMAIN=barormebel.uz
APP_USER=barormebel
APP_DIR=/home/$APP_USER/barormebel
REPO=https://github.com/Arabjonoff/baror-furniture.git
DB_NAME=barormebel
DB_USER=barormebel
ADMIN_EMAIL=admin@$DOMAIN

if [ "$(id -u)" -ne 0 ]; then echo "root sifatida ishga tushiring (sudo)"; exit 1; fi

echo ">>> [1/9] Tizim paketlari..."
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3 python3-venv python3-dev build-essential \
    postgresql postgresql-contrib libpq-dev nginx git curl \
    certbot python3-certbot-nginx

echo ">>> [2/9] '$APP_USER' foydalanuvchisi..."
id -u "$APP_USER" &>/dev/null || adduser --disabled-password --gecos "" "$APP_USER"

echo ">>> [3/9] PostgreSQL bazasi..."
read -rsp "Yangi DB paroli ('$DB_USER' uchun): " DB_PASSWORD; echo
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'Asia/Tashkent';"

echo ">>> [4/9] Repo klonlash..."
if [ -d "$APP_DIR/.git" ]; then
  sudo -u "$APP_USER" git -C "$APP_DIR" pull --ff-only origin main
else
  sudo -u "$APP_USER" git clone "$REPO" "$APP_DIR"
fi

echo ">>> [5/9] venv + kutubxonalar..."
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/venv"
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

echo ">>> [6/9] .env..."
if [ ! -f "$APP_DIR/.env" ]; then
  SECRET=$("$APP_DIR/venv/bin/python" -c "import secrets; print(secrets.token_urlsafe(50))")
  cat > "$APP_DIR/.env" <<EOF
SECRET_KEY=$SECRET
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
USE_SQLITE=False
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432
EOF
  chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
  chmod 600 "$APP_DIR/.env"
  echo "    .env yaratildi (SECRET_KEY avtomatik)."
else
  echo "    .env allaqachon mavjud — o'zgartirilmadi."
fi

echo ">>> [7/9] migrate + collectstatic..."
cd "$APP_DIR"
sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" manage.py migrate --noinput
sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" manage.py collectstatic --noinput

# nginx (www-data) statik/media fayllarni o'qiy olishi uchun ruxsatlar
# ($HOME odatda 0750 — www-data kira olmaydi, natijada CSS/JS 403 bo'ladi)
sudo -u "$APP_USER" mkdir -p "$APP_DIR/media"
chmod o+x "/home/$APP_USER"
chmod -R o+rX "$APP_DIR/staticfiles" "$APP_DIR/media"

echo ">>> [8/9] systemd + sudoers + nginx..."
cp "$APP_DIR/deploy/barormebel.service" /etc/systemd/system/barormebel.service
# CI deploy uchun: barormebel foydalanuvchisi parolsiz faqat shu xizmatni qayta ishga tushira oladi
echo "$APP_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart barormebel, /usr/bin/systemctl status barormebel" \
  > /etc/sudoers.d/barormebel
chmod 440 /etc/sudoers.d/barormebel
systemctl daemon-reload
systemctl enable --now barormebel

cp "$APP_DIR/deploy/nginx-barormebel.conf" /etc/nginx/sites-available/barormebel
ln -sf /etc/nginx/sites-available/barormebel /etc/nginx/sites-enabled/barormebel
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo ">>> [9/9] HTTPS (Let's Encrypt)..."
if certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos -m "$ADMIN_EMAIL" --redirect; then
  echo "    HTTPS sertifikat o'rnatildi."
else
  echo "    !! Certbot xato berdi. DNS ($DOMAIN -> server IP) tayyor bo'lgach qayta uruning:"
  echo "       certbot --nginx -d $DOMAIN -d www.$DOMAIN --redirect"
fi

echo
echo "============================================================"
echo " TAYYOR.  Sayt: https://$DOMAIN"
echo " Admin yaratish:"
echo "   sudo -u $APP_USER $APP_DIR/venv/bin/python $APP_DIR/manage.py createsuperuser"
echo " Loglar:  journalctl -u barormebel -f"
echo "============================================================"
