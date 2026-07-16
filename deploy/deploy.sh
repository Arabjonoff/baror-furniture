#!/usr/bin/env bash
# Har bir relizda ishlaydigan deploy skripti.
# CI (GitHub Actions) `barormebel` foydalanuvchi sifatida SSH orqali chaqiradi.
set -euo pipefail

APP_DIR=/home/barormebel/barormebel
cd "$APP_DIR"

echo ">>> Kod yangilanmoqda..."
git pull --ff-only origin main

echo ">>> Kutubxonalar..."
venv/bin/pip install --quiet --upgrade pip
venv/bin/pip install --quiet -r requirements.txt

echo ">>> Migratsiyalar..."
venv/bin/python manage.py migrate --noinput

echo ">>> Statik fayllar..."
venv/bin/python manage.py collectstatic --noinput

echo ">>> Xizmat qayta ishga tushirilmoqda..."
sudo /usr/bin/systemctl restart barormebel

echo ">>> TAYYOR: $(date '+%Y-%m-%d %H:%M:%S')"
