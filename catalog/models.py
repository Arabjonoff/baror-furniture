from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Mahsulot kategoriyasi (masalan: Divan, Stol, Stul, Karavot, Shkaf, Komod)."""

    name = models.CharField('nomi', max_length=100)
    slug = models.SlugField('slug', max_length=120, unique=True, blank=True)
    parent = models.ForeignKey(
        'self',
        verbose_name='ota-kategoriya',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
    )
    image = models.ImageField('rasm', upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField('faolmi', default=True)

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Material(models.Model):
    """Mahsulot materiali (masalan: Yog'och, LDSP, Metall) — admin orqali boshqariladi."""

    name = models.CharField('nomi', max_length=100, unique=True)
    slug = models.SlugField('slug', max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiallar'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class RoomType(models.Model):
    """Xona turi (masalan: Mehmonxona, Yotoqxona, Ofis) — admin orqali boshqariladi."""

    name = models.CharField('nomi', max_length=100, unique=True)
    slug = models.SlugField('slug', max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = 'Xona turi'
        verbose_name_plural = 'Xona turlari'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Sotuvdagi mebel mahsuloti."""

    name = models.CharField('nomi', max_length=200)
    slug = models.SlugField('slug', max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        verbose_name='kategoriya',
        on_delete=models.PROTECT,
        related_name='products',
    )
    description = models.TextField('tavsif', blank=True)
    price = models.DecimalField('narx', max_digits=12, decimal_places=2)
    old_price = models.DecimalField(
        'chegirmagacha narx', max_digits=12, decimal_places=2, blank=True, null=True
    )
    width = models.DecimalField('kengligi (sm)', max_digits=6, decimal_places=1, blank=True, null=True)
    height = models.DecimalField('balandligi (sm)', max_digits=6, decimal_places=1, blank=True, null=True)
    depth = models.DecimalField('chuqurligi (sm)', max_digits=6, decimal_places=1, blank=True, null=True)
    material = models.ForeignKey(
        Material,
        verbose_name='material',
        on_delete=models.SET_NULL,
        related_name='products',
        blank=True,
        null=True,
    )
    room_type = models.ForeignKey(
        RoomType,
        verbose_name='xona turi',
        on_delete=models.SET_NULL,
        related_name='products',
        blank=True,
        null=True,
    )
    weight = models.DecimalField('og\'irligi (kg)', max_digits=6, decimal_places=1, blank=True, null=True)
    stock = models.IntegerField('ombordagi qoldiq', default=0)
    is_available = models.BooleanField('sotuvdami', default=True)
    is_featured = models.BooleanField("bosh sahifada ko'rsatilsinmi", default=False)
    views_count = models.PositiveIntegerField("ko'rilganlar soni", default=0)
    created_at = models.DateTimeField('yaratilgan vaqti', auto_now_add=True)
    updated_at = models.DateTimeField('yangilangan vaqti', auto_now=True)

    class Meta:
        verbose_name = 'Mahsulot'
        verbose_name_plural = 'Mahsulotlar'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_discount_percent(self):
        """Chegirma foizini hisoblaydi (old_price bo'lmasa yoki narxdan kichik bo'lsa 0)."""
        if not self.old_price or self.old_price <= self.price:
            return 0
        return round((self.old_price - self.price) / self.old_price * 100)

    @property
    def in_stock(self):
        return self.stock > 0


class Banner(models.Model):
    """Bosh sahifadagi banner/slayder yozuvi — admin orqali boshqariladi."""

    eyebrow = models.CharField('kichik sarlavha', max_length=50, blank=True)
    title = models.CharField('sarlavha', max_length=200)
    description = models.CharField('tavsif', max_length=300, blank=True)
    image = models.ImageField('fon rasmi', upload_to='slides/', blank=True, null=True)
    button_text = models.CharField('tugma matni', max_length=50, blank=True)
    button_link = models.CharField('tugma havolasi', max_length=200, blank=True)
    order = models.PositiveIntegerField('tartib raqami', default=0)
    is_active = models.BooleanField('faolmi', default=True)

    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Bannerlar'
        ordering = ['order']

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    """Mahsulotning qo'shimcha rasmlari (bittadan ko'p)."""

    product = models.ForeignKey(
        Product,
        verbose_name='mahsulot',
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField('rasm', upload_to='products/')
    is_main = models.BooleanField('asosiy rasmmi', default=False)
    order = models.PositiveIntegerField('tartib raqami', default=0)

    class Meta:
        verbose_name = 'Mahsulot rasmi'
        verbose_name_plural = 'Mahsulot rasmlari'
        ordering = ['order']

    def __str__(self):
        return f'{self.product.name} — rasm {self.order}'


class ProductColor(models.Model):
    """Mahsulotning rang variantlari."""

    product = models.ForeignKey(
        Product,
        verbose_name='mahsulot',
        on_delete=models.CASCADE,
        related_name='colors',
    )
    color_name = models.CharField('rang nomi', max_length=50)
    color_hex = models.CharField('HEX kod', max_length=7)
    image = models.ImageField('rasm', upload_to='products/colors/', blank=True, null=True)

    class Meta:
        verbose_name = 'Mahsulot rangi'
        verbose_name_plural = 'Mahsulot ranglari'
        ordering = ['color_name']

    def __str__(self):
        return f'{self.product.name} — {self.color_name}'
