# Barormebel — serverga joylashtirish (deployment) va CI/CD

Server: **Ubuntu VPS** · Domen: **barormebel.uz** · Stek: **gunicorn + systemd + nginx + PostgreSQL + Let's Encrypt (HTTPS)**

Deploy avtomatlashtirilgan: `main` bran­chga har push → **GitHub Actions** CI (tekshiruv) → muvaffaqiyatli bo'lsa serverga SSH orqali avtomatik deploy.

---

## 0. Oldindan (bir marta)

1. **DNS**: domen provayderingizda `barormebel.uz` va `www.barormebel.uz` uchun **A-record**larni server IP manzilingizga yo'naltiring. `dig barormebel.uz +short` server IP ni ko'rsatishi kerak (tarqalishi bir necha soat olishi mumkin).
2. **⚠️ Root parolini almashtiring** — u chatda oshkor bo'lgan. Serverga kirib: `passwd`.
3. Server bilan HTTPS ishlashi uchun 80 va 443 portlar ochiq bo'lsin (`ufw allow 'Nginx Full'` va `ufw allow OpenSSH`).

---

## 1. Serverni bir marta tayyorlash (bootstrap)

Serverga root sifatida kiring va quyidagini bajaring:

```bash
# repozitoriyani vaqtincha klonlab, bootstrap skriptini ishga tushiramiz
git clone https://github.com/Arabjonoff/baror-furniture.git /tmp/baror
sudo bash /tmp/baror/deploy/bootstrap.sh
```

Skript so'raydi: **DB paroli** (yangi, xohlagan parolingizni kiriting — bu PostgreSQL `barormebel` foydalanuvchisi uchun). Qolganini o'zi qiladi:

- Kerakli paketlar (python, postgres, nginx, certbot)
- `barormebel` foydalanuvchisi
- PostgreSQL bazasi va foydalanuvchisi
- Repo klonlanadi: `/home/barormebel/barormebel`
- venv + kutubxonalar
- `.env` (SECRET_KEY avtomatik, DEBUG=False, PostgreSQL)
- `migrate` + `collectstatic`
- systemd xizmati (`barormebel`) — ishga tushadi
- nginx sozlamasi
- **HTTPS** sertifikat (Let's Encrypt) — DNS tayyor bo'lsa

> Agar certbot xato bersa (DNS hali tarqalmagan), keyin qayta uring:
> `certbot --nginx -d barormebel.uz -d www.barormebel.uz --redirect`

**Admin foydalanuvchi yarating:**

```bash
sudo -u barormebel /home/barormebel/barormebel/venv/bin/python \
  /home/barormebel/barormebel/manage.py createsuperuser
```

Shu bosqichdan keyin sayt **https://barormebel.uz** da ishlaydi.

---

## 2. CI/CD ni ulash (avtomatik deploy)

Har push'da serverga avtomatik deploy bo'lishi uchun GitHub Actions serverga SSH kalit orqali kiradi.

### 2.1. Deploy uchun SSH kalit yarating (o'z kompyuteringizda)

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f barormebel_deploy -N ""
```
Ikki fayl hosil bo'ladi: `barormebel_deploy` (maxfiy kalit) va `barormebel_deploy.pub` (ochiq kalit).

### 2.2. Ochiq kalitni serverga qo'shing (root sifatida serverda)

```bash
sudo mkdir -p /home/barormebel/.ssh
echo "BU_YERGA_barormebel_deploy.pub_TARKIBI" | sudo tee -a /home/barormebel/.ssh/authorized_keys
sudo chown -R barormebel:barormebel /home/barormebel/.ssh
sudo chmod 700 /home/barormebel/.ssh
sudo chmod 600 /home/barormebel/.ssh/authorized_keys
```

### 2.3. GitHub Secrets qo'shing

GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret nomi        | Qiymati                                             |
|--------------------|-----------------------------------------------------|
| `SSH_HOST`         | server IP manzili                                   |
| `SSH_USER`         | `barormebel`                                        |
| `SSH_PRIVATE_KEY`  | `barormebel_deploy` faylining **to'liq** tarkibi    |
| `SSH_PORT`         | `22` (agar boshqacha bo'lmasa — ixtiyoriy)          |

> Maxfiy kalitni (`barormebel_deploy`) hech kimga bermang, faqat GitHub Secret sifatida qo'ying.

### 2.4. Tayyor 🎉

Endi `main` branchga har push:
1. **CI** ishlaydi (`python manage.py check`, migratsiyalar, testlar).
2. Muvaffaqiyatli bo'lsa **Deploy** ishlaydi: serverda `git pull → pip install → migrate → collectstatic → xizmatni restart`.

Qo'lda ishga tushirish: GitHub → **Actions → Deploy → Run workflow**.

---

## 3. Kundalik ish

| Vazifa | Buyruq |
|--------|--------|
| Loglar (jonli) | `journalctl -u barormebel -f` |
| Xizmat holati | `systemctl status barormebel` |
| Qo'lda restart | `sudo systemctl restart barormebel` |
| Qo'lda deploy | serverda `bash /home/barormebel/barormebel/deploy/deploy.sh` |
| nginx loglari | `tail -f /var/log/nginx/error.log` |
| Sertifikat yangilash | avtomatik (certbot timer); tekshirish: `certbot renew --dry-run` |

---

## 4. Zaxira (backup)

`media/` (yuklangan rasmlar) va PostgreSQL bazasini muntazam zaxiralang:

```bash
# Baza
sudo -u postgres pg_dump barormebel > barormebel_$(date +%F).sql
# Media
tar czf media_$(date +%F).tar.gz -C /home/barormebel/barormebel media
```

> `media/` va `db.sqlite3` git'ga yuklanmaydi — ular faqat serverda.

---

## 5. Muammolarni bartaraf etish

- **502 Bad Gateway** → gunicorn ishlamayapti: `systemctl status barormebel`, `journalctl -u barormebel -n 50`.
- **Statik/CSS ko'rinmayapti** → `collectstatic` bajarilganini va nginx `alias` yo'lini tekshiring.
- **CSRF xato (forma yuborishda)** → `.env` dagi `CSRF_TRUSTED_ORIGINS` da `https://barormebel.uz` borligini tekshiring.
- **Certbot xato** → DNS server IP ga ishora qilishini kuting, so'ng `certbot --nginx -d barormebel.uz -d www.barormebel.uz`.
- **Deploy Actions'da xato** → SSH secretlarini va serverdagi `authorized_keys` ni tekshiring.
