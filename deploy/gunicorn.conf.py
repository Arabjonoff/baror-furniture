"""Gunicorn konfiguratsiyasi — barormebel (systemd orqali ishga tushiriladi)."""

import multiprocessing

# nginx shu manzilga proxy qiladi
bind = "127.0.0.1:8001"

# CPU yadrolariga qarab worker soni (kichik VPS uchun 3 yetarli)
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)
timeout = 60
graceful_timeout = 30
keepalive = 5

# Loglar journald (systemd) ga chiqadi
accesslog = "-"
errorlog = "-"
loglevel = "info"
