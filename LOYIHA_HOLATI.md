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

### Bosqich 12 — Logo joylashtirish

`static/img/logo.svg` (brend wordmark, 1600×123, jigarrang/orange) header va footer'ga qo'yildi.
- Header: matnli "Barormebel" o'rniga SVG rasm (balandligi 42px)
- Footer: matnli logo o'rniga SVG (balandligi 52px)
- Rasmsiz bo'lsa avvalgidek matn (`.logo-img`, `.footer-logo-img` CSS)

### Bosqich 13 — Buyurtma himoyasi (login talab qilinadi)

`orders/views.py` `checkout_view`ga `@login_required` qo'shildi. Endi tizimga **kirmagan foydalanuvchi buyurtma bera olmaydi** — avtomatik login sahifasiga yo'naltiriladi. Buyurtma har doim tizimga kirgan foydalanuvchiga tegishli (`user=request.user`).

### Bosqich 14 — Material va Xona turi — alohida modellar (admin boshqaradi)

Ilgari `Product.material` va `Product.room_type` qattiq yozilgan `choices` edi (admin o'zgartira olmasdi). Endi alohida **modellar**:
- Yangi **`Material`** va **`RoomType`** modellari (`name`, `slug`)
- `Product.material` / `room_type` endi ular uchun **ForeignKey** (`SET_NULL`)
- Admin panelda ro'yxatdan o'tkazildi — admin qo'shadi/tahrirlaydi/o'chiradi
- Maxsus data-migratsiya (`0003_material_roomtype.py`) bilan mavjud qiymatlar saqlab qolindi
- `views.py` filtr (slug bo'yicha), `product_list.html` va `product_detail.html` moslandi

### Bosqich 15 — Banner rasmi ko'rinmaslik muammosi (ad-blocker)

**Muammo:** admin banner rasmi yuklaydi, lekin saytda ko'rinmaydi. `curl` bilan 200, brauzerda esa yo'q.
**Sabab (aniqlangan):** rasm yo'li `/media/**banners**/...` edi. **Reklama bloklovchilar** (uBlock/AdBlock/Brave) URL'da "banner" so'zi bo'lsa uni reklama deb bloklaydi (`responseStatus=0`).
**Yechim:** yuklash papkasi `banners/` → **`slides/`** ga o'zgartirildi (`Banner.image upload_to='slides/'`), mavjud fayllar ko'chirildi, baza yangilandi (`0004_alter_banner_image`).
> **Eslatma:** URL/fayl nomida "banner", "ad" kabi so'zlardan qoching — bloklovchilar to'sadi.

### Bosqich 16 — Banner UI/UX (rasm + matn boshqaruvi)

`home.html` va CSS:
- Bannerda **rasm bo'lsa** — toza ko'rsatiladi; **matn/tugma ham kiritilgan bo'lsa** (`has-content`) — rasm ustida o'qilishi uchun qoraytiruvchi qatlam bilan chiqadi
- **Rasmsiz** banner — gradient fon + matn (avvalgidek)
- Balandlik **16:6 nisbatga** moslandi (`aspect-ratio`, `cover`) — qirqilmaydi/yo'lakcha yo'q
- Mobil ekranda matnli bannerlar siqilmasligi uchun `min-height: 320px`

### Bosqich 17 — O'xshash mahsulotlar (detail sahifada)

`product_detail` view kengaytirildi: bo'lim doim to'ladi (4 tagacha) — avval **o'sha kategoriya**, yetmasa **o'sha xona turi/material (tag)**, u ham yetmasa **boshqa mavjud mahsulotlar**. Shablonda "O'xshash mahsulotlar" bo'limi allaqachon bor edi.

### Bosqich 18 — Profil mukammallashtirish (avatar + UI/UX)

User modeliga qo'shildi: **`avatar`** (`media/avatars/`), **`email`**, **`birth_date`**, **`gender`**. Avatar yo'q bo'lsa ism bosh harfi ko'rsatiladi (`initial` property).
Profil sahifasi to'liq qayta dizayn qilindi (`profile.html`, CSS):
- **Hero header** — gradient fon, dumaloq avatar, ism, telefon, a'zolik sanasi, statistika plitalari (buyurtma/manzil/sevimli soni)
- Avatar yuklash (jonli preview bilan), fokus effektli forma maydonlari
- Telefon o'zgarmas (login ID), amal tugmalari (parol/chiqish)
- Django admin ham yangi maydonlar bilan yangilandi

### Bosqich 19 — Bonus ballar, bildirishnomalar, ko'rilgan mahsulotlar

- **🎁 Bonus ballar (sodiqlik dasturi):** `User.bonus_points`. Har buyurtmada summaning **1%** avtomatik qo'shiladi (`checkout_view`). Profilda alohida karta.
- **🔔 Bildirishnoma sozlamalari:** `notify_sms`, `notify_email` (SMS/email marketing roziligi). Profil formasida belgilash oynachalari.
- **👁 Ko'rilgan mahsulotlar:** sessiyada kuzatiladi (`recently_viewed`, 12 tagacha), profil pastida karta grid.

### Bosqich 20 — Maxsus boshqaruv paneli (Dashboard) — `/boshqaruv/`

Django admin o'rniga zamonaviy, brendga mos **maxsus dashboard** (`dashboard` app):
- **📊 Statistika:** 4 ta ko'rsatkich (daromad, buyurtmalar, mahsulotlar, mijozlar), 7 kunlik daromad grafigi, holat taqsimoti, oxirgi buyurtmalar, kam qoldiq, eng ko'p sotilganlar
- **🧾 Buyurtmalar:** filtr + qidiruv, rangli badge'lar, tafsilot + holat/to'lovni yangilash
- **🛋️ Mahsulotlar:** qidiruv + filtr, qo'shish/tahrir/o'chirish (`ProductDashboardForm`)
- **👥 Mijozlar:** buyurtma soni, xarid summasi, bonus bilan ro'yxat
- To'q sidebar, rangli badge, mobilga moslashuvchan; faqat **staff** kira oladi (`@staff_member_required`)
- Sayt header'ida "Boshqaruv" tugmasi (staff uchun), yon menyuda yangi buyurtmalar soni (context processor)
- Fayllar: `dashboard/` (views, urls, context_processors, 6 shablon), `catalog/forms_dashboard.py`, `static/css/dashboard.css`

### Bosqich 21 — GitHub'ga yuklash

Loyiha git repozitoriyaga aylantirildi va **https://github.com/Arabjonoff/baror-furniture** ga push qilindi (`main` branch).
- `.gitignore` kengaytirildi; **`.env`, `db.sqlite3`, `media/`, `venv/`, `.claude/settings.local.json`** yuklanmadi (maxfiylik saqlandi)
- `README.md` (o'rnatish + deployment yo'riqnomasi) va `.env.example` qo'shildi
- **Keyingi qadam:** foydalanuvchi serverga deploy qiladi — serverda `.env` qo'lda yaratiladi (`DEBUG=False`, yangi `SECRET_KEY`, `ALLOWED_HOSTS`, PostgreSQL), `media/` qayta yuklanadi

### Bosqich 22 — SEO (qidiruv tizimlariga moslash)

Sayt Google/Yandex uchun indekslashga tayyorlandi:
- **`sitemap.xml`** — Django `django.contrib.sitemaps` frameworki (`catalog/sitemaps.py`): statik sahifalar, faol kategoriyalar va sotuvdagi mahsulotlar (mahsulotlarda `lastmod`). URL: `/sitemap.xml`. `INSTALLED_APPS`ga `django.contrib.sitemaps` qo'shildi.
- **`robots.txt`** — `/robots.txt` (`templates/robots.txt`, `TemplateView`). Xaridorga xos sahifalar (`/savat/`, `/hisob/`, `/boshqaruv/`, `/admin/`...) `Disallow`, sitemap havolasi ko'rsatilgan.
- **Meta teglar** — `base.html`da `description`, `keywords`, `robots`, **canonical** havola va to'liq **Open Graph** + Twitter Card teglari (blok orqali sahifalar o'zining meta'sini beradi).
- **Sahifaga xos meta** — mahsulot sahifasi (`product_detail.html`) tavsifdan `description` va `og:image` (asosiy rasm), katalog/kategoriya sahifasi (`product_list.html`) o'z tavsifi bilan.
- Modellarga **`get_absolute_url()`** qo'shildi (`Product`, `Category`) — sitemap va kanonik havolalar uchun.

### Bosqich 23 — Promokod (chegirma kodlari)

To'liq promokod tizimi:
- **`PromoCode` modeli** (`orders/models.py`) — kod, chegirma turi (**foiz** yoki **belgilangan summa**), qiymati, foiz uchun **maksimal chegirma**, **minimal buyurtma summasi**, amal muddati (`valid_from`/`valid_until`), **foydalanish limiti** (`usage_limit`/`used_count`), faollik. `is_valid(total)` va `discount_for(total)` metodlari (chegirma summadan oshmaydi, kod avtomatik BOSH HARFga o'tadi).
- **Savatda qo'llash** — promokod sessiyada saqlanadi (`orders/promo.py`). Savat sahifasida qo'llash/olib tashlash formasi, chegirma va yakuniy summa alohida ko'rsatiladi. URL'lar: `/savat/promokod/`, `/savat/promokod/olib-tashlash/`.
- **Checkout** — buyurtma yaratishda chegirma qayta tekshiriladi, `Order.promo_code` + `Order.discount` saqlanadi, `total_price` chegirmadan **keyingi** summa. Promokod `used_count` oshiriladi, bonus ball yakuniy summadan hisoblanadi. Buyurtmadan keyin promokod sessiyadan tozalanadi.
- **Order** modeliga `promo_code`, `discount` maydonlari va `subtotal` property qo'shildi. Checkout va tasdiqlash sahifalari chegirmani ko'rsatadi.
- **Admin** — `PromoCodeAdmin` (kod, chegirma, limit, foydalanilgan soni; `fieldsets` bilan). CSS: savat/checkout summasi kartochka ko'rinishida, `.btn-secondary`, promokod formasi uslublari.

### Bosqich 24 — Savat sahifasi UI/UX qayta dizayn

Eski oddiy jadval (har o'zgarishda butun sahifa qayta yuklanardi) zamonaviy dizaynga almashtirildi:
- **Ikki ustunli tartib** — chapda mahsulot kartochkalari, o'ngda **yopishib turuvchi (sticky)** buyurtma xulosasi.
- Har mahsulot: rasm eskizi, nomi, rang chipi, **dumaloq miqdor stepperi (− soni +)**, qator jami + dona narxi, savatcha ikonkasi bilan o'chirish.
- **To'liq AJAX** — miqdor o'zgarishi va o'chirish sahifani yangilamaydi; qator jami, chegirma va yakuniy summa jonli hisoblanadi (server `_summary_payload` qaytaradi). O'chirilgan kartochka silliq surilib yo'qoladi.
- Xulosada promokod (yashil banner), Mahsulotlar/Chegirma/Yetkazib berish/Jami qatorlari, "Buyurtmani rasmiylashtirish", ishonch belgilari.
- `cart/views.py` AJAX javoblari boyitildi (`item_total`, `subtotal`, `discount`, `final_total`, `quantity`, `empty`). Yangi JS savat moduli, yangi CSS.
- **Muhim CSS saboq:** `.cart-total-line{display:flex}` HTML `hidden` atributini bosib ketardi — `.cart-total-line[hidden]{display:none}` qo'shildi.

### Bosqich 25 — Mahsulot kartochkasi (savatga qo'shish → miqdor stepperi)

Kartochka zamonaviylashtirildi va **savatga qo'shgandan keyin +/- va soni kartada ko'rinadi**:
- "Savatga qo'shish" tugmasi (savatcha ikonkasi bilan) bosilgach **AJAX** orqali miqdor stepperiga aylanadi — sahifa yangilanmaydi.
- **+** oshiradi, **−** kamaytiradi; **1 dan pastga tushsa** mahsulot savatdan chiqadi va yana "Savatga qo'shish" tugmasiga qaytadi. Stokdan oshib bo'lmaydi.
- Boshlang'ich holat serverdan render qilinadi: `cart.context_processors` endi `cart_quantities` ({product_id: miqdor}, rangsiz yozuvlar) beradi; savatda bo'lgan mahsulot kartochkasi darhol stepper ko'rsatadi (reload'дан keyin ham).
- Header savat soni har amalda jonli yangilanadi. Yangi `dict_get` shablon filtri, `cart_add` javobiga `item_quantity` qo'shildi.
- Kartaning burchagi yumaloqlashtirildi (`--radius-lg`), hover soyasi kuchaytirildi. Stepper uslublari savat sahifasi bilan bir xil (`.qty-stepper`).
- **Diqqat:** `.product-card-cart [hidden]{display:none !important}` — aks holda `.qty-stepper{display:flex}` `[hidden]`ni yengib, tugma va stepper birga chiqib qolardi.
- **Flexbox saboq:** stepper ichidagi `<input>`ning standart `min-width:auto` qiymati uni ichki kengligidan kichraytirmasdi va **`+` tugmasi karta chetidan chiqib ketardi**. `.product-card-stepper .qty-input`ga `min-width:0` qo'shildi — endi input to'g'ri kichrayadi, `+` doim ko'rinadi.

### Bosqich 26 — Serverga joylashtirish (deployment) + CI/CD

Loyiha production'ga tayyorlandi. Stek: **gunicorn + systemd + nginx + PostgreSQL + Let's Encrypt (HTTPS)**, domen **barormebel.uz**. To'liq yo'riqnoma: `DEPLOYMENT.md`.

- **Production sozlamalari** (`settings.py`) — `DEBUG=False` bo'lganda: `SECURE_PROXY_SSL_HEADER` (nginx orqasida), secure cookie'lar, HSTS, `X_FRAME_OPTIONS`, `SECURE_CONTENT_TYPE_NOSNIFF`. `CSRF_TRUSTED_ORIGINS` env orqali.
- **`requirements.txt`** — `gunicorn` qo'shildi. **`.env.example`** production izohlari bilan yangilandi (PostgreSQL, CSRF).
- **`deploy/`** papkasi:
  - `bootstrap.sh` — serverni **bir marta** tayyorlaydi (paketlar, `barormebel` user, PostgreSQL baza, repo, venv, `.env` avtomatik SECRET_KEY, migrate, collectstatic, systemd, nginx, certbot HTTPS)
  - `deploy.sh` — har relizda: `git pull → pip install → migrate → collectstatic → systemctl restart`
  - `barormebel.service` (systemd/gunicorn), `nginx-barormebel.conf`, `gunicorn.conf.py`
- **CI/CD** (`.github/workflows/`):
  - `ci.yml` — har push/PR: `check`, `makemigrations --check`, `migrate`, `test` (SQLite)
  - `deploy.yml` — CI muvaffaqiyatli tugagach `main`'да serverga SSH (appleboy/ssh-action) orqali `deploy.sh` chaqiradi. Secretlar: `SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY`, `SSH_PORT`.
- **`.gitattributes`** — `.sh` va `deploy/*` fayllar doim **LF** (Windows CRLF Linux skriptlarini buzadi).
- **Xavfsizlik qarori:** root parol kodда/CI'да saqlanmaydi — deploy SSH kalitlari + GitHub Secrets orqali. Serverni root talab qiladigan bir martalik `bootstrap.sh` ni foydalanuvchi o'zi ishga tushiradi.

### Bosqich 27 — Serverga real deploy va CI/CD ulash (JONLI) ✅

Loyiha **https://barormebel.uz** da jonli ishlaydi. Server: Ubuntu VPS (`5.104.108.235`). Bootstrap muvaffaqiyatli o'tdi, HTTPS (Let's Encrypt) o'rnatildi, CI/CD to'liq ishlaydi (`main`'ga push → CI → avtomatik deploy).

**Deploy paytida yuzaga kelgan real muammolar va saboqlar:**

1. **Statik fayllar 403 (CSS/JS/dizayn umuman ishlamadi).** Sabab: `$HOME` (`/home/barormebel`) ruxsati `0750` — nginx (`www-data`) papkaga kira olmadi. Yechim: `chmod o+x /home/barormebel` + `chmod -R o+rX staticfiles media`. **Repoga qo'shildi** (`bootstrap.sh`, `deploy.sh`) va `settings.py`ga `FILE_UPLOAD_PERMISSIONS=0o644` (yangi media yuklamalar o'qishga ochiq bo'lishi uchun).
2. **GitHub Secrets — har biri ALOHIDA qo'shiladi.** Boshida bitta noto'g'ri nomli secret qo'shilgan edi → deploy `Error: missing server host` berdi. `SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY` — uchtasi alohida, aniq nomlar bilan.
3. **SSH publickey rad etildi** (`unable to authenticate, attempted methods [none publickey]`). Sabab: ochiq kalit serverdagi `/home/barormebel/.ssh/authorized_keys` ga to'g'ri qo'shilmagan edi. Yechim: kalitni `tee` bilan aniq yozib, `.ssh` 700 / `authorized_keys` 600 / egasi `barormebel` qilish.
4. **Diagnostika usuli:** GitHub Actions loglari saqlangan `git credential` (token) orqali API'dan o'qildi — `actions/jobs/{id}/logs`. `gh` CLI o'rnatilmagan bo'lsa ham log ko'rish mumkin.

**Server buyruqlari (kundalik):**
- Loglar: `journalctl -u barormebel -f`
- Restart: `sudo systemctl restart barormebel`
- Superuser: `sudo -u barormebel /home/barormebel/barormebel/venv/bin/python /home/barormebel/barormebel/manage.py createsuperuser`

> **Eslatma:** root parolini almashtirish tavsiya etilgan (sozlash paytida oshkor bo'lgan).

## Test/kirish ma'lumotlari

- **🌐 Jonli sayt (production):** https://barormebel.uz · Dashboard: https://barormebel.uz/boshqaruv/ · Admin: https://barormebel.uz/admin/
- **Server:** Ubuntu VPS `5.104.108.235` (gunicorn+systemd+nginx+PostgreSQL). Deploy avtomatik (GitHub'ga push).
- **Admin panel (lokal):** `http://127.0.0.1:8000/admin/`
- **Superuser:** telefon `+998901112233`, parol `admin123`
- Test mahsulotlari: "Yumshoq divan Milano", "Yozuv stoli Oslo", "Karavot Comfort 160x200" (kategoriyalar: Divan, Stol, Karavot)
- **Test promokodlari:** `BAROR10` (10% chegirma, min. 1 000 000 so'm), `MINUS500` (500 000 so'm chegirma) — savatda sinab ko'rish uchun
- **SEO:** `http://127.0.0.1:8000/sitemap.xml`, `http://127.0.0.1:8000/robots.txt`

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
2. ~~**Sodiqlik dasturi (bonus ballar)**~~ — ✅ bajarildi (Bosqich 19)
3. ~~**Maxsus boshqaruv paneli (dashboard)**~~ — ✅ bajarildi (Bosqich 20)
4. **Sharh va reyting** — mahsulotga baho
5. **Taqqoslash** — bir nechta mebelni solishtirish
6. ~~**Chegirma/promokod tizimi**~~ — ✅ bajarildi (Bosqich 23). Qoldi: bonus ballarni xaridda ishlatish
7. **Telegram bot** — adminga yangi buyurtma haqida xabarnoma; SMS/email marketing (rozilik allaqachon yig'ilyapti — Bosqich 19)
8. ~~**SEO**~~ — ✅ bajarildi (Bosqich 22): meta teglar, sitemap, robots.txt, Open Graph
9. **Yetkazib berish narxi kalkulyatori** — viloyatga qarab
10. **Online to'lov** (Bosqich 7) — Payme/Click/Uzum, faqat alohida so'ralganda boshlanadi
11. **Dashboard qo'shimchalari** — sana oralig'i filtri, Excelga eksport, mahsulot rasmini shu paneldan yuklash

## Bilinadigan kichik narsalar

- **Banner rasmlari** endi `media/slides/` papkasida (ad-blocker sababli "banners"dan ko'chirilgan — Bosqich 15). Tavsiya etilgan o'lcham: **~1600×600 px, gorizontal, 16:6 nisbat**. URL/fayl nomida "banner", "ad" so'zlaridan qoching.
- Ba'zi test mahsulotlarning `stock` qiymati checkout testlari tufayli kamaygan bo'lishi mumkin — real ishlatishda admin panel yoki yangi **dashboard** (`/boshqaruv/`) orqali yangilang.
- `media/` va `db.sqlite3` git'ga yuklanmaydi (Bosqich 21) — serverda alohida boshqariladi.

## Sessiyada aniqlangan muhim saboqlar

- **Ad-blocker "banner" so'zini bloklaydi** (Bosqich 15) — media/statik yo'llarida "banner", "ad", "promo" kabi so'zlardan qoching.
- **Django dev-server media serveri ishonchli** — Windows'da ham 200 qaytaradi; muammo odatda brauzer/kengaytma tomonida bo'ladi (Resource Timing `responseStatus`/`transferSize` bilan tekshiring).
- **CSS: inline element'ga `width`/`height` qo'llanmaydi** — progress bar `.fill`ga `display:block` kerak bo'ldi (dashboard).
- **Django admin custom User** — yangi maydon qo'shilganda `fieldsets`ni ham yangilash kerak.