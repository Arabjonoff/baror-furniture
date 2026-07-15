from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from cart.cart import Cart

from .forms import CheckoutForm
from .models import Order, OrderItem


@login_required
def checkout_view(request):
    """Savatdan buyurtma berish jarayoni: forma to'ldirish, stock tekshirish, Order yaratish.

    Faqat tizimga kirgan foydalanuvchilar uchun — mehmonlar login sahifasiga yo'naltiriladi.
    """
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, "Savatingiz bo'sh. Buyurtma berish uchun avval mahsulot tanlang.")
        return redirect('cart:detail')

    initial = {}
    if request.user.is_authenticated:
        initial['full_name'] = request.user.full_name
        initial['phone'] = request.user.phone_number
        default_address = request.user.addresses.filter(is_default=True).first()
        if default_address:
            initial['saved_address'] = default_address.pk
            initial['region'] = default_address.region
            initial['district'] = default_address.district
            initial['address'] = default_address.street

    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            saved_address = form.cleaned_data.get('saved_address')
            region = saved_address.region if saved_address else form.cleaned_data['region']
            district = saved_address.district if saved_address else form.cleaned_data['district']
            address = saved_address.street if saved_address else form.cleaned_data['address']

            insufficient = [
                item['product'].name for item in cart if item['quantity'] > item['product'].stock
            ]
            if insufficient:
                messages.error(
                    request,
                    "Ombordagi qoldiq yetarli emas: " + ', '.join(insufficient),
                )
            else:
                with transaction.atomic():
                    order = Order.objects.create(
                        user=request.user,
                        full_name=form.cleaned_data['full_name'],
                        phone=form.cleaned_data['phone'],
                        region=region,
                        district=district,
                        address=address,
                        delivery_type=form.cleaned_data['delivery_type'],
                        comment=form.cleaned_data['comment'],
                        total_price=cart.get_total_price(),
                    )
                    for item in cart:
                        product = item['product']
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            color=item['color'],
                            price=item['price'],
                            quantity=item['quantity'],
                        )
                        product.stock -= item['quantity']
                        product.save(update_fields=['stock'])

                    # Sodiqlik dasturi: buyurtma summasining 1% bonus ball sifatida qo'shiladi
                    earned = int(cart.get_total_price() // 100)
                    if earned:
                        request.user.bonus_points = F('bonus_points') + earned
                        request.user.save(update_fields=['bonus_points'])
                        request.user.refresh_from_db(fields=['bonus_points'])

                    cart.clear()

                if earned:
                    messages.success(request, f"Buyurtmangiz uchun {earned} bonus ball qo'shildi!")
                return redirect('orders:confirmation', order_id=order.id)
    else:
        form = CheckoutForm(initial=initial, user=request.user)

    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'orders/checkout.html', context)


def order_confirmation_view(request, order_id):
    """Buyurtma tasdiqlash sahifasi — buyurtma raqami va tafsilotlari."""
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'orders/confirmation.html', {'order': order})


@login_required
def order_list_view(request):
    """Tizimga kirgan foydalanuvchining buyurtmalari tarixi."""
    orders = request.user.orders.all()
    return render(request, 'orders/list.html', {'orders': orders})


@login_required
def order_detail_view(request, order_id):
    """Foydalanuvchining o'z buyurtmasi tafsilotlari."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'orders/confirmation.html', {'order': order})
