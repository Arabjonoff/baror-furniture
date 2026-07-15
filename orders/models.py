from django.conf import settings
from django.db import models

from accounts.models import phone_validator
from catalog.models import Product


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
    total_price = models.DecimalField('jami summa', max_digits=12, decimal_places=2, default=0)
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
