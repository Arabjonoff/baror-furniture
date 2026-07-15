from .wishlist import Wishlist


def wishlist(request):
    """Sevimlilarni har bir shablonda mavjud qiladi — header'dagi son va yurakcha holati uchun."""
    wl = Wishlist(request)
    return {'wishlist': wl, 'wishlist_product_ids': wl.product_ids}
