# Barormebel — mebel do'koni

🌐 **Jonli sayt:** [barormebel.uz](https://barormebel.uz)

O'zbek tilidagi mebel do'koni uchun Django e-commerce platformasi: katalog, savat, sevimlilar,
buyurtmalar, foydalanuvchi profili (bonus ballar, ko'rilgan mahsulotlar) va zamonaviy maxsus
boshqaruv paneli (dashboard).

Serverga joylashtirish va CI/CD bo'yicha to'liq yo'riqnoma: [`DEPLOYMENT.md`](DEPLOYMENT.md).

## Texnologiyalar

- Python 3 / Django 5.2
- SQLite (dev) yoki PostgreSQL (production)
- Telefon raqami orqali autentifikatsiya (custom User modeli)

## Asosiy imkoniyatlar

- 🛋️ Mahsulotlar katalogi — kategoriya, material, xona turi bo'yicha filtr
- 🛒 Savat va sevimlilar (AJAX)
- 📦 Buyurtma berish (faqat ro'yxatdan o'tganlar uchun)
- 👤 Foydalanuvchi profili — avatar, bonus ballar, bildirishnoma sozlamalari, ko'rilgan mahsulotlar tarixi
- 🎁 Sodiqlik dasturi — har buyurtmadan 1% bonus ball
- 📊 Maxsus boshqaruv paneli (`/boshqaruv/`) — statistika, buyurtma va mahsulot boshqaruvi, mijozlar

## O'rnatish (lokal)

```bash
# 1. Virtual muhit
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 2. Kutubxonalar
pip install -r requirements.txt

# 3. Muhit fayli
copy .env.example .env       # Windows (Linux/Mac: cp)
# .env ichidagi qiymatlarni to'ldiring

# 4. Migratsiyalar
python manage.py migrate

# 5. Admin foydalanuvchi
python manage.py createsuperuser

# 6. Serverni ishga tushirish
python manage.py runserver
```

Sayt: http://127.0.0.1:8000/ · Boshqaruv paneli: http://127.0.0.1:8000/boshqaruv/

## Production (serverga yuklash) uchun eslatmalar

- `.env` da `DEBUG=False`, yangi `SECRET_KEY` va to'g'ri `ALLOWED_HOSTS` qo'ying
- PostgreSQL uchun `USE_SQLITE=False` va DB sozlamalarini to'ldiring
- `python manage.py collectstatic` bilan statik fayllarni yig'ing
- Statik/media fayllarni nginx yoki WhiteNoise orqali xizmat qiling
- WSGI server (gunicorn/uwsgi) ishlating

> `db.sqlite3` va `media/` git'ga yuklanmaydi — serverda o'z ma'lumotlar bazangiz va yuklamalaringiz bo'ladi.
