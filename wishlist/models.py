from django.conf import settings
from django.db import models

from catalog.models import Product


class WishlistItem(models.Model):
    """Ro'yxatdan o'tgan foydalanuvchining sevimli mahsuloti."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='foydalanuvchi',
        on_delete=models.CASCADE,
        related_name='wishlist_items',
    )
    product = models.ForeignKey(
        Product,
        verbose_name='mahsulot',
        on_delete=models.CASCADE,
        related_name='wishlist_items',
    )
    created_at = models.DateTimeField("qo'shilgan vaqti", auto_now_add=True)

    class Meta:
        verbose_name = 'Sevimli mahsulot'
        verbose_name_plural = 'Sevimli mahsulotlar'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product_wishlist'),
        ]

    def __str__(self):
        return f'{self.user} — {self.product.name}'
