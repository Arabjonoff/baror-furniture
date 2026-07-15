# Barormebel — loyiha holati

> Ushbu fayl loyihaning umumiy maqsadini va hozirgacha bajarilgan barcha ishlarni tasvirlaydi. Ertaga (yoki keyingi safar) ishga qaytganda shu fayldan boshlang — qayerda to'xtaganingiz va nima qilinganini shu yerdan bilib olasiz.

## Loyiha nima uchun kerak

**Barormebel** — O'zbekiston bozori uchun mo'ljallangan online mebel do'koni veb-sayti. Maqsad:

- Foydalanuvchi mebel kataloglarini ko'radi, filtrlaydi va qidiradi
- Mahsulotni savatga qo'shadi (ro'yxatdan o'tmasdan ham)
- Telefon raqami orqali ro'yxatdan o'tadi/kiradi
- Buyurtma beradi (hozircha faqat naqd — yetkazib berishda to'lov)
- Admin (do'kon egasi) mahsulot, kategoriya, buyurtma va foydalanuvchilarni Django admin panel orqali boshqaradi

## Texnologik stek

- **Backend:** Django 5.2 (Python 3.14)
- **Ma'lumotlar bazasi:** hozircha SQLite (`db.sqlite3`, dev uchun), PostgreSQL'ga tayyor (`.env` orqali `USE_SQLITE=False` qilinsa)
- **Frontend:** Django Templates + toza CSS/JS (React yo'q, framework yo'q)
- **Rasm:** Pillow, `media/` papkasida saqlanadi

### Muhim texnik eslatma

Boshida Django 5.0.14 bilan boshlangan edi, lekin Python 3.14 bilan **admin panel** 500 xato berdi (`Context.__copy__` xatosi — Django 5.0 va Python 3.14 mos kelmasligi). **Django 5.2 LTS**ga yangilandi va muammo hal bo'ldi. `requirements.txt`da `Django>=5.2,<5.3` deb yozilgan.

## Loyiha strukturasi

```
barormebel/
├── manage.py
├── requirements.txt
├── .env / .env.example
├── mebel_shop/          — asosiy Django konfiguratsiyasi (settings.py, urls.py)
├── catalog/              — kategoriya, mahsulot, banner (bosh sahifa/katalog)
├── cart/                 — sessiya asosidagi savat
├── wishlist/             — sevimlilar (mehmonlar: sessiya, foydalanuvchilar: baza)
├── orders/                — buyurtma va checkout
├── accounts/              — custom User (telefon orqali), manzillar
├── templates/base.html   — umumiy shablon (header, footer, hamburger)
├── static/css/style.css  — yagona dizayn tizimi
├── static/js/main.js     — AJAX savat, lightbox, slider, hamburger
└── media/                — yuklangan rasmlar (banners/, categories/, products/)
```

## Bajarilgan bosqichlar (1–10)

### Bosqich 1 — Loyiha asosi
Django loyihasi (`mebel_shop`) va 4 ta app (`catalog`, `cart`, `orders`, `accounts`) yaratildi. `.env` orqali sozlanadigan DB, `uz` tili, `Asia/Tashkent` vaqt zonasi, static/media sozlamalari.

### Bosqich 2 — Ma'lumotlar modellari
`catalog/models.py`:
- **Category** — nomi, slug (avto), ota-kategoriya (self-FK), rasm, faolmi
- **Product** — nomi, narx/chegirma, o'lchamlar, material, xona turi, stock, `get_discount_percent()`, `in_stock` property
- **ProductImage** — mahsulot rasmlari (bittadan ko'p)
- **ProductColor** — rang variantlari (nomi + HEX)

### Bosqich 3 — Katalog: ro'yxat, detal, filtr, qidiruv
`catalog/views.py`: `home`, `product_list` (filtr: narx, material, xona turi, rang, mavjudlik; saralash; qidiruv; pagination 12 tadan), `product_detail` (galereya, ranglar, o'xshash mahsulotlar, `views_count` oshirish).

### Bosqich 4 — Savat (Cart)
`cart/cart.py` — sessiya asosidagi `Cart` klassi (`add`, `remove`, `update`, `__iter__`, `__len__`, `get_total_price`, `clear`). AJAX orqali "Savatga qo'shish" (sahifa yangilanmaydi), header'da savat soni real vaqtda yangilanadi.

### Bosqich 5 — Foydalanuvchilar (accounts)
Custom **User** modeli — `phone_number` (`+998XXXXXXXXX` formatida) login sifatida, email yo'q. `UserManager` (`create_user`, `create_superuser`). **Address** modeli (viloyat, tuman, ko'cha, mo'ljal, telefon, `is_default`). Ro'yxatdan o'tish/kirish/chiqish, profil (ma'lumot yangilash, parol o'zgartirish, manzillar CRUD).

> **Muhim:** Custom User modeli sabab loyiha boshida bazani qayta yaratishga to'g'ri keldi (Django qoidasi: `AUTH_USER_MODEL` faqat birinchi migratsiyadan oldin o'zgartiriladi).

### Bosqich 6 — Buyurtma (Orders) va Checkout
`orders/models.py`: **Order** (mehmon buyurtmasi ham bo'ladi — `user` ixtiyoriy, yetkazib berish ma'lumotlari, `delivery_type`/`status`/`payment_status`/`payment_method` choices) va **OrderItem** (narx buyurtma paytida "muzlatiladi").

Checkout jarayoni: savatdan → forma (ro'yxatdan o'tgan foydalanuvchi uchun saqlangan manzil avtomatik tanlanadi/to'ldiriladi) → **stock yetarliligini tekshiradi** → `Order`+`OrderItem` yaratadi → stock kamaytiradi → savatni tozalaydi → tasdiqlash sahifasiga o'tadi.

### Bosqich 7 — Online to'lov — **O'TKAZIB YUBORILDI (ataylab)**
Hozircha faqat naqd to'lov. `Order.payment_method`/`payment_status` choices kelajakda Payme/Click/Uzum qo'shish uchun tayyor qilib qo'yilgan. **Foydalanuvchi buni keyinroq, kerak bo'lganda alohida so'raydi.**

### Bosqich 8 — Admin panel
`catalog/admin.py`, `orders/admin.py`, `accounts/admin.py` to'liq sozlandi:
- Product: `list_editable` (narx, stock), filtr, qidiruv, rasm/rang inline (preview bilan), `prepopulated_fields` (slug)
- Order: holat/to'lov holatini ro'yxatdan tahrirlash, `OrderItem` inline, filtrlar
- **Banner** modeli qo'shildi (Bosqich 9'da) — bosh sahifa slayderini boshqarish uchun
- Custom User uchun to'g'ri `UserAdmin` (parol xavfsiz hash qilinadi)
- Admin sarlavhalari: "Barormebel boshqaruv paneli"

### Bosqich 9 — Dizayn va sayqallash
- Yagona dizayn tizimi (CSS o'zgaruvchilar: issiq jigarrang/bej palitra, tipografiya, tugma variantlari)
- Responsive header: hamburger menyu (mobil), "Katalog" ustida kategoriyalar dropdown, qidiruv, savat soni
- Kengaytirilgan footer: aloqa, ijtimoiy tarmoq (SVG ikonkalar), kategoriyalar
- **Bosh sahifa banner/slayder** — admin panelda `Banner` modeli orqali to'liq boshqariladi (sarlavha, tavsif, rasm, tugma, tartib, faollik)
- Mahsulot kartochkasi hover effekti (rasm zoom)
- Bo'sh holatlar (`.empty-state` komponenti) — savat, qidiruv natijasi, buyurtmalar uchun
- AJAX tugma loading holati (spinner)
- **Mahsulot galereyasi lightbox** — rasmga bosganda to'liq ekranda ochiladi, zoom, strelkalar, `Esc` bilan yopish
- **Summalar formatlash** — barcha narxlar `4 500 000 so'm` kabi bo'sh joy bilan ajratilgan holda ko'rsatiladi (`catalog/templatetags/catalog_extras.py` dagi `money` filtri)

### Bosqich 10 — Sevimlilar (Wishlist)

Yangi `wishlist` app'i. Savat kabi ikki rejimda ishlaydi:

- **Mehmon:** sevimlilar sessiyada saqlanadi (`wishlist/wishlist.py` — `Wishlist` klassi)
- **Ro'yxatdan o'tgan:** bazada (`WishlistItem` modeli, `user`+`product` unique)
- **Login paytida** sessiyadagi sevimlilar avtomatik bazaga ko'chadi (`user_logged_in` signali, `wishlist/signals.py`)

UI: mahsulot kartochkasi va mahsulot sahifasida yurakcha tugmasi (AJAX toggle, sahifa yangilanmaydi), header'da "Sevimlilar (n)" havolasi (soni real vaqtda yangilanadi), `/sevimlilar/` sahifasi (bo'sh holat bilan), admin panelda ro'yxat. Sevimlilar sahifasida yurakcha o'chirilsa kartochka darhol yo'qoladi.

URL'lar: `/sevimlilar/` (ro'yxat), `/sevimlilar/belgilash/<id>/` (POST, toggle). Context processor: `wishlist.context_processors.wishlist` (`wishlist` va `wishlist_product_ids` har shablonda).

### Bosqich 11 — Sevimlilar (yurakcha) iconi UI/UX yaxshilash

Yurakcha tugmasi dizayni butun sayt bo'ylab qayta ishlandi (faqat `static/css/style.css`, HTML/JS tegilmadi):

- **Overlap bug tuzatildi** — mahsulot kartochkasida yurakcha `top-right`da, "Tugagan" (out-of-stock) badge ham aynan shu joyda edi va ustma-ust tushardi. "Tugagan" badge **pastki-chap** burchakka ko'chirildi (`.badge-outofstock`), yurakcha o'z burchagida yolg'iz qoldi. `-25%` chegirma badge esa yuqori-chapda.
- **Rang mantiqi to'g'rilandi** — `.wishlist-btn` asosiy rangi endi neytral `--color-muted` (nofaol holat "bosilmagan"dek ko'rinadi), faol bo'lganda (`.is-active`) `--color-heart` (brend jigarrang) to'liq bo'yaladi. Ilgari doim jigarrang bo'lib, allaqachon tanlangandek adashtirardi.
- **Ko'rinish sayqallandi** — og'ir ikki qatlamli soya olib tashlanib, dizayn tizimining `--shadow-sm`/`--shadow-md` va **frosted (blur) oq doira** ishlatildi. Overlay 40→38px, detail 46→44px.
- **Detail variant** — mahsulot sahifasida sarlavha yonidagi tugma faol/hover holatida chegara va fon brend rangga o'tadi (`.wishlist-btn-detail.is-active`), kartochka bilan bir xil uslub.

Brauzerda tekshirildi: bosh sahifa, katalog, mahsulot sahifasi, sevimlilar (bo'sh va to'la) — barchasi izchil.

## Test/kirish ma'lumotlari

- **Admin panel:** `http://127.0.0.1:8000/admin/`
- **Superuser:** telefon `+998901112233`, parol `admin123`
- Test mahsulotlari: "Yumshoq divan Milano", "Yozuv stoli Oslo", "Karavot Comfort 160x200" (kategoriyalar: Divan, Stol, Karavot)

## Loyihani ishga tushirish

```bash
cd barormebel
source venv/Scripts/activate   # yoki venv\Scripts\activate.bat (cmd)
python manage.py runserver
```

Sayt: `http://127.0.0.1:8000/`

## Keyinroq qo'shish mumkin bo'lgan g'oyalar (ixtiyoriy, hali boshlanmagan)

Foydalanuvchi tomonidan aytilgan, lekin hali amalga oshirilmagan:

1. ~~**Sevimlilar (Wishlist)**~~ — ✅ bajarildi (Bosqich 10)
2. **Sharh va reyting** — mahsulotga baho
3. **Taqqoslash** — bir nechta mebelni solishtirish
4. **Chegirma/promokod tizimi**
5. **Telegram bot** — adminga yangi buyurtma haqida xabarnoma
6. **SEO** — meta teglar, sitemap, chiroyli URL'lar
7. **Yetkazib berish narxi kalkulyatori** — viloyatga qarab
8. **Online to'lov** (Bosqich 7) — Payme/Click/Uzum, faqat alohida so'ralganda boshlanadi

## Bilinadigan kichik narsalar

- `media/` papkadagi ba'zi test rasmlar (masalan noto'g'ri o'lchamdagi banner rasmlari) tozalab qo'yilgan — bannerlarga hozircha rasm yo'q, standart gradient fon ishlatiladi. Banner uchun tavsiya etilgan o'lcham: **~1600×6a00 px, gorizontal**.
- Ba'zi test mahsulotlarning `stock` qiymati checkout testlari tufayli kamaygan bo'lishi mumkin — real ishlatishda admin panel orqali yangilang.
