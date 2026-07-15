from catalog.models import Product

from .models import WishlistItem

WISHLIST_SESSION_ID = 'wishlist'


class Wishlist:
    """Sevimlilar ro'yxati — mehmonlar uchun sessiyada, ro'yxatdan o'tganlar uchun bazada saqlanadi."""

    def __init__(self, request):
        self.session = request.session
        self.user = request.user if request.user.is_authenticated else None
        if self.user is None and WISHLIST_SESSION_ID not in self.session:
            self.session[WISHLIST_SESSION_ID] = []

    def _session_ids(self):
        return self.session.get(WISHLIST_SESSION_ID, [])

    @property
    def product_ids(self):
        """Sevimlilardagi mahsulot id'lari — shablonda yurakchani belgilash uchun."""
        if self.user:
            return set(
                WishlistItem.objects.filter(user=self.user).values_list('product_id', flat=True)
            )
        return set(self._session_ids())

    def toggle(self, product):
        """Mahsulot sevimlilarda bo'lsa o'chiradi, bo'lmasa qo'shadi. Qo'shilgan bo'lsa True qaytaradi."""
        if self.user:
            item, created = WishlistItem.objects.get_or_create(user=self.user, product=product)
            if not created:
                item.delete()
            return created

        ids = self._session_ids()
        if product.id in ids:
            ids.remove(product.id)
            added = False
        else:
            ids.append(product.id)
            added = True
        self.session[WISHLIST_SESSION_ID] = ids
        self.session.modified = True
        return added

    def products(self):
        """Sevimlilardagi mahsulotlar (oxirgi qo'shilgani birinchi)."""
        if self.user:
            items = (WishlistItem.objects.filter(user=self.user)
                     .select_related('product').prefetch_related('product__images'))
            return [item.product for item in items]
        ids = self._session_ids()
        products_map = Product.objects.prefetch_related('images').in_bulk(ids)
        return [products_map[pk] for pk in reversed(ids) if pk in products_map]

    def __len__(self):
        if self.user:
            return WishlistItem.objects.filter(user=self.user).count()
        return len(self._session_ids())

    @staticmethod
    def merge_session_to_user(request, user):
        """Login paytida sessiyadagi sevimlilarni foydalanuvchi bazasiga ko'chiradi."""
        ids = request.session.pop(WISHLIST_SESSION_ID, [])
        if not ids:
            return
        for product in Product.objects.filter(pk__in=ids):
            WishlistItem.objects.get_or_create(user=user, product=product)
        request.session.modified = True
