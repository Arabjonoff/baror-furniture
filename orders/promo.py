"""Savatga qo'llanilgan promokodni sessiyada boshqarish uchun yordamchi funksiyalar."""

from .models import PromoCode

PROMO_SESSION_ID = 'promo_code'


def get_applied_promo(request, total):
    """Sessiyadagi promokodni oladi va joriy summaga amal qilishini tekshiradi.

    Amal qilsa PromoCode obyektini, aks holda None qaytaradi. Endi haqiqiy
    bo'lmagan (o'chirilgan yoki muddati tugagan) kod sessiyadan tozalanadi.
    """
    code = request.session.get(PROMO_SESSION_ID)
    if not code:
        return None
    try:
        promo = PromoCode.objects.get(code=code)
    except PromoCode.DoesNotExist:
        request.session.pop(PROMO_SESSION_ID, None)
        return None
    ok, _ = promo.is_valid(total)
    if not ok:
        return None
    return promo


def promo_context(request, total):
    """Shablonlar uchun promokod konteksti: {promo, discount, final_total}."""
    promo = get_applied_promo(request, total)
    discount = promo.discount_for(total) if promo else 0
    return {
        'promo': promo,
        'discount': discount,
        'final_total': total - discount,
    }
