from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from accounts.models import phone_validator
from catalog.models import Product


class PromoCode(models.Model):
    """Chegirma promokodi — admin yaratadi, xaridor savatda qo'llaydi."""

    TYPE_PERCENT = 'foiz'
    TYPE_FIXED = 'summa'
    DISCOUNT_TYPE_CHOICES = [
        (TYPE_PERCENT, 'Foiz (%)'),
        (TYPE_FIXED, "Belgilangan summa (so'm)"),
    ]

    code = models.CharField('promokod', max_length=30, unique=True)
    description = models.CharField('izoh', max_length=200, blank=True)
    discount_type = models.CharField(
        'chegirma turi', max_length=10, choices=DISCOUNT_TYPE_CHOICES, default=TYPE_PERCENT
    )
    discount_value = models.DecimalField('chegirma qiymati', max_digits=12, decimal_places=2)
    max_discount = models.DecimalField(
        'maksimal chegirma (faqat foiz uchun)', max_digits=12, decimal_places=2,
        blank=True, null=True,
        help_text="Foizli chegirma uchun eng yuqori summa (ixtiyoriy).",
    )
    min_order_amount = models.DecimalField(
        'minimal buyurtma summasi', max_digits=12, decimal_places=2, default=0
    )
    valid_from = models.DateTimeField('amal boshlanishi', blank=True, null=True)
    valid_until = models.DateTimeField('amal tugashi', blank=True, null=True)
    usage_limit = models.PositiveIntegerField(
        'umumiy foydalanish limiti', blank=True, null=True,
        help_text="Bo'sh qoldirilsa — cheksiz.",
    )
    used_count = models.PositiveIntegerField('foydalanilgan soni', default=0)
    is_active = models.BooleanField('faolmi', default=True)
    created_at = models.DateTimeField('yaratilgan vaqti', auto_now_add=True)

    class Meta:
        verbose_name = 'Promokod'
        verbose_name_plural = 'Promokodlar'
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def is_valid(self, total, now=None):
        """Promokod berilgan savat summasiga amal qiladimi — (bool, xabar) qaytaradi."""
        now = now or timezone.now()
        if not self.is_active:
            return False, 'Bu promokod faol emas.'
        if self.valid_from and now < self.valid_from:
            return False, 'Promokod hali kuchga kirmagan.'
        if self.valid_until and now > self.valid_until:
            return False, 'Promokod muddati tugagan.'
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False, 'Promokod foydalanish limiti tugagan.'
        if total < self.min_order_amount:
            return False, (
                f"Bu promokod {int(self.min_order_amount):,}".replace(',', ' ')
                + " so'mdan yuqori buyurtmalarga amal qiladi."
            )
        return True, ''

    def discount_for(self, total):
        """Berilgan summa uchun chegirma miqdorini hisoblaydi (summadan oshib ketmaydi)."""
        if self.discount_type == self.TYPE_PERCENT:
            amount = total * self.discount_value / Decimal('100')
            if self.max_discount:
                amount = min(amount, self.max_discount)
        else:
            amount = self.discount_value
        amount = min(amount, total)
        return amount.quantize(Decimal('0.01'))


class Order(models.Model):
    """Foydalanuvchi yoki mehmon tomonidan berilgan buyurtma."""

    DELIVERY_TASHKENT = 'tashkent'
    DELIVERY_REGION = 'viloyat'
    DELIVERY_PICKUP = 'pickup'
    DELIVERY_TYPE_CHOICES = [
        (DELIVERY_TASHKENT, 'Toshkent ichi'),
        (DELIVERY_REGION, 'Viloyat'),
        (DELIVERY_PICKUP, 'Olib ketish'),
    ]

    STATUS_NEW = 'yangi'
    STATUS_CONFIRMED = 'tasdiqlangan'
    STATUS_SHIPPING = 'yolda'
    STATUS_DELIVERED = 'yetkazildi'
    STATUS_CANCELLED = 'bekor_qilingan'
    STATUS_CHOICES = [
        (STATUS_NEW, 'Yangi'),
        (STATUS_CONFIRMED, 'Tasdiqlangan'),
        (STATUS_SHIPPING, "Yo'lda"),
        (STATUS_DELIVERED, 'Yetkazildi'),
        (STATUS_CANCELLED, 'Bekor qilingan'),
    ]

    PAYMENT_PENDING = 'kutilmoqda'
    PAYMENT_PAID = 'tolangan'
    PAYMENT_CANCELLED = 'bekor'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, 'Kutilmoqda'),
        (PAYMENT_PAID, "To'langan"),
        (PAYMENT_CANCELLED, 'Bekor'),
    ]

    PAYMENT_METHOD_CASH = 'naqd'
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_CASH, "Naqd — yetkazib berishda to'lov"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='foydalanuvchi',
        on_delete=models.SET_NULL,
        related_name='orders',
        blank=True,
        null=True,
    )
    full_name = models.CharField('ism', max_length=150)
    phone = models.CharField('telefon', max_length=13, validators=[phone_validator])
    region = models.CharField('viloyat', max_length=100)
    district = models.CharField('tuman', max_length=100)
    address = models.CharField('manzil', max_length=255)
    delivery_type = models.CharField(
        'yetkazib berish turi', max_length=20, choices=DELIVERY_TYPE_CHOICES
    )
    promo_code = models.CharField('qo\'llanilgan promokod', max_length=30, blank=True)
    discount = models.DecimalField('chegirma summasi', max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField('jami summa (chegirmadan keyin)', max_digits=12, decimal_places=2, default=0)
    status = models.CharField('holat', max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    payment_status = models.CharField(
        "to'lov holati", max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING
    )
    payment_method = models.CharField(
        "to'lov usuli", max_length=20, choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_METHOD_CASH
    )
    comment = models.TextField('izoh', blank=True)
    created_at = models.DateTimeField('yaratilgan vaqti', auto_now_add=True)

    class Meta:
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'
        ordering = ['-created_at']

    def __str__(self):
        return f'Buyurtma #{self.id}'

    @property
    def subtotal(self):
        """Chegirmagacha bo'lgan summa."""
        return self.total_price + self.discount


class OrderItem(models.Model):
    """Buyurtmadagi bitta mahsulot qatori — narx buyurtma paytidagi holatda saqlanadi."""

    order = models.ForeignKey(Order, verbose_name='buyurtma', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        Product, verbose_name='mahsulot', on_delete=models.PROTECT, related_name='order_items'
    )
    color = models.CharField('rang', max_length=50, blank=True)
    price = models.DecimalField('narx (buyurtma paytida)', max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField('miqdor', default=1)

    class Meta:
        verbose_name = 'Buyurtma qatori'
        verbose_name_plural = 'Buyurtma qatorlari'

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def get_cost(self):
        return self.price * self.quantity
