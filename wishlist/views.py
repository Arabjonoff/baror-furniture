from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Product

from .wishlist import Wishlist


def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def wishlist_detail(request):
    """Sevimlilar sahifasi — belgilangan mahsulotlar ro'yxati."""
    wishlist = Wishlist(request)
    return render(request, 'wishlist/detail.html', {'products': wishlist.products()})


def wishlist_toggle(request, product_id):
    """Mahsulotni sevimlilarga qo'shadi yoki o'chiradi. AJAX so'rov bo'lsa JSON qaytaradi."""
    product = get_object_or_404(Product, pk=product_id)

    if request.method != 'POST':
        return redirect('catalog:product_detail', slug=product.slug)

    wishlist = Wishlist(request)
    added = wishlist.toggle(product)
    if added:
        message = f'"{product.name}" sevimlilarga qo\'shildi.'
    else:
        message = f'"{product.name}" sevimlilardan o\'chirildi.'

    if _is_ajax(request):
        return JsonResponse({
            'ok': True,
            'added': added,
            'wishlist_count': len(wishlist),
            'message': message,
        })

    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER') or 'wishlist:detail')
