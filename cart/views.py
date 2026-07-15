from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Product

from .cart import Cart


def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def cart_detail(request):
    """Savat sahifasi — mahsulotlar, miqdorlar va jami summa."""
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})


def cart_add(request, product_id):
    """Mahsulotni savatga qo'shadi. AJAX so'rov bo'lsa JSON qaytaradi."""
    product = get_object_or_404(Product, pk=product_id, is_available=True)

    if request.method != 'POST':
        return redirect('catalog:product_detail', slug=product.slug)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1
    color = request.POST.get('color', '')

    cart = Cart(request)
    cart.add(product=product, quantity=quantity, color=color)
    message = f'"{product.name}" savatga qo\'shildi.'

    if _is_ajax(request):
        return JsonResponse({
            'ok': True,
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price()),
            'message': message,
        })

    messages.success(request, message)
    return redirect('catalog:product_detail', slug=product.slug)


def cart_remove(request, product_id):
    """Mahsulotni savatdan o'chiradi."""
    product = get_object_or_404(Product, pk=product_id)
    color = request.POST.get('color', '')

    cart = Cart(request)
    cart.remove(product, color=color)

    if _is_ajax(request):
        return JsonResponse({'ok': True, 'cart_count': len(cart), 'cart_total': str(cart.get_total_price())})

    messages.success(request, "Mahsulot savatdan o'chirildi.")
    return redirect('cart:detail')


def cart_update(request, product_id):
    """Savatdagi mahsulot miqdorini yangilaydi."""
    product = get_object_or_404(Product, pk=product_id)

    if request.method != 'POST':
        return redirect('cart:detail')

    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1
    color = request.POST.get('color', '')

    cart = Cart(request)
    cart.update(product, quantity, color=color)

    if _is_ajax(request):
        return JsonResponse({'ok': True, 'cart_count': len(cart), 'cart_total': str(cart.get_total_price())})

    return redirect('cart:detail')
