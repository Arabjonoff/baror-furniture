from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, DecimalField, Q, Sum
from django.db.models.deletion import ProtectedError
from django.db.models.functions import Coalesce, TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User
from catalog.models import Banner, Category, Material, Product, RoomType
from orders.models import Order, PromoCode
from wishlist.models import WishlistItem

from .forms import (
    AddressFormSet, BannerForm, CategoryForm, MaterialForm, ProductColorFormSet,
    ProductForm, ProductImageFormSet, PromoCodeForm, RoomTypeForm, UserCreateForm,
    UserEditForm,
)

LOW_STOCK_THRESHOLD = 5


def _money(value):
    return Decimal(value or 0)


def _form_view(request, form_class, instance, *, active, title, subtitle, list_url, redirect_url, msg):
    """Oddiy ModelForm bo'limlari uchun umumiy create/edit ko'rinishi."""
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, msg)
            return redirect(redirect_url)
    else:
        form = form_class(instance=instance)
    return render(request, 'dashboard/generic_form.html', {
        'active': active,
        'form': form,
        'form_title': title,
        'form_subtitle': subtitle,
        'list_url': list_url,
        'instance': instance,
    })


def _delete_view(request, obj, *, redirect_url, label):
    """Umumiy o'chirish (POST) — himoyalangan bog'lanish bo'lsa xato beradi."""
    if request.method == 'POST':
        try:
            obj.delete()
            messages.success(request, f'{label} o\'chirildi.')
        except ProtectedError:
            messages.error(
                request,
                f'{label} o\'chirib bo\'lmadi — u boshqa yozuvlar (masalan, buyurtma) bilan bog\'langan.',
            )
    return redirect(redirect_url)


# =============================================================
#  STATISTIKA (bosh sahifa)
# =============================================================
@staff_member_required
def index(request):
    orders = Order.objects.all()
    active_orders = orders.exclude(status=Order.STATUS_CANCELLED)

    total_revenue = active_orders.aggregate(
        s=Coalesce(Sum('total_price'), Decimal(0), output_field=DecimalField())
    )['s']

    stats = {
        'revenue': total_revenue,
        'orders_total': orders.count(),
        'orders_new': orders.filter(status=Order.STATUS_NEW).count(),
        'products_total': Product.objects.count(),
        'low_stock': Product.objects.filter(stock__lte=LOW_STOCK_THRESHOLD).count(),
        'customers': User.objects.filter(is_staff=False).count(),
    }

    today = timezone.localdate()
    start = today - timedelta(days=6)
    daily = (
        active_orders.filter(created_at__date__gte=start)
        .annotate(d=TruncDate('created_at'))
        .values('d')
        .annotate(total=Sum('total_price'), cnt=Count('id'))
    )
    daily_map = {row['d']: row for row in daily}
    weekday_names = ['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh', 'Ya']
    chart = []
    for i in range(7):
        day = start + timedelta(days=i)
        row = daily_map.get(day)
        chart.append({
            'label': weekday_names[day.weekday()],
            'date': day,
            'total': _money(row['total']) if row else Decimal(0),
            'count': row['cnt'] if row else 0,
        })
    chart_max = max((c['total'] for c in chart), default=Decimal(0)) or Decimal(1)
    for c in chart:
        c['percent'] = int(c['total'] / chart_max * 100)

    status_counts = {row['status']: row['c'] for row in orders.values('status').annotate(c=Count('id'))}
    status_breakdown = [
        {'code': code, 'label': label, 'count': status_counts.get(code, 0)}
        for code, label in Order.STATUS_CHOICES
    ]

    top_products = (
        Product.objects.annotate(sold=Coalesce(Sum('order_items__quantity'), 0))
        .filter(sold__gt=0)
        .order_by('-sold')[:5]
    )

    context = {
        'active': 'index',
        'stats': stats,
        'chart': chart,
        'status_breakdown': status_breakdown,
        'recent_orders': orders.select_related('user')[:8],
        'low_stock_products': Product.objects.filter(stock__lte=LOW_STOCK_THRESHOLD)
        .select_related('category').order_by('stock')[:6],
        'top_products': top_products,
    }
    return render(request, 'dashboard/index.html', context)


# =============================================================
#  BUYURTMALAR
# =============================================================
@staff_member_required
def orders_list(request):
    orders = Order.objects.select_related('user').prefetch_related('items')
    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)
    query = request.GET.get('q', '').strip()
    if query:
        orders = orders.filter(
            Q(id__icontains=query) | Q(full_name__icontains=query) | Q(phone__icontains=query)
        )

    context = {
        'active': 'orders',
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'selected_status': status,
        'query': query,
    }
    return render(request, 'dashboard/orders.html', context)


@staff_member_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product'), pk=order_id
    )

    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_payment = request.POST.get('payment_status')
        valid_status = dict(Order.STATUS_CHOICES)
        valid_payment = dict(Order.PAYMENT_STATUS_CHOICES)
        changed = False
        if new_status in valid_status and new_status != order.status:
            order.status = new_status
            changed = True
        if new_payment in valid_payment and new_payment != order.payment_status:
            order.payment_status = new_payment
            changed = True
        if changed:
            order.save(update_fields=['status', 'payment_status'])
            messages.success(request, 'Buyurtma holati yangilandi.')
        return redirect('dashboard:order_detail', order_id=order.id)

    context = {
        'active': 'orders',
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
        'payment_choices': Order.PAYMENT_STATUS_CHOICES,
    }
    return render(request, 'dashboard/order_detail.html', context)


@staff_member_required
def order_delete(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        order.delete()
        messages.success(request, f'Buyurtma #{order_id} o\'chirildi.')
    return redirect('dashboard:orders')


# =============================================================
#  MAHSULOTLAR (rasm + rang formsetlari bilan)
# =============================================================
@staff_member_required
def products_list(request):
    products = Product.objects.select_related('category').prefetch_related('images')
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(name__icontains=query)
    category = request.GET.get('category', '')
    if category:
        products = products.filter(category__slug=category)

    context = {
        'active': 'products',
        'products': products,
        'categories': Category.objects.all(),
        'selected_category': category,
        'query': query,
        'low_stock_threshold': LOW_STOCK_THRESHOLD,
    }
    return render(request, 'dashboard/products.html', context)


def _product_form(request, product, title):
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        image_fs = ProductImageFormSet(request.POST, request.FILES, instance=product, prefix='images')
        color_fs = ProductColorFormSet(request.POST, request.FILES, instance=product, prefix='colors')
        if form.is_valid() and image_fs.is_valid() and color_fs.is_valid():
            product = form.save()
            image_fs.instance = product
            image_fs.save()
            color_fs.instance = product
            color_fs.save()
            messages.success(request, f'"{product.name}" saqlandi.')
            return redirect('dashboard:products')
    else:
        form = ProductForm(instance=product)
        image_fs = ProductImageFormSet(instance=product, prefix='images')
        color_fs = ProductColorFormSet(instance=product, prefix='colors')

    return render(request, 'dashboard/product_form.html', {
        'active': 'products',
        'form': form,
        'image_formset': image_fs,
        'color_formset': color_fs,
        'title': title,
        'product': product,
    })


@staff_member_required
def product_create(request):
    return _product_form(request, None, 'Yangi mahsulot')


@staff_member_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return _product_form(request, product, product.name)


@staff_member_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return _delete_view(request, product, redirect_url='dashboard:products', label=f'"{product.name}"')


# =============================================================
#  KATEGORIYALAR
# =============================================================
@staff_member_required
def categories_list(request):
    categories = Category.objects.select_related('parent').annotate(pcount=Count('products'))
    return render(request, 'dashboard/categories.html', {
        'active': 'categories', 'categories': categories,
    })


@staff_member_required
def category_create(request):
    return _form_view(
        request, CategoryForm, None, active='categories',
        title='Yangi kategoriya', subtitle="Kategoriya ma'lumotlari",
        list_url='dashboard:categories', redirect_url='dashboard:categories',
        msg="Kategoriya qo'shildi.",
    )


@staff_member_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    return _form_view(
        request, CategoryForm, category, active='categories',
        title=category.name, subtitle='Kategoriyani tahrirlash',
        list_url='dashboard:categories', redirect_url='dashboard:categories',
        msg='Kategoriya yangilandi.',
    )


@staff_member_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    return _delete_view(request, category, redirect_url='dashboard:categories', label=f'"{category.name}"')


# =============================================================
#  MATERIALLAR
# =============================================================
@staff_member_required
def materials_list(request):
    materials = Material.objects.annotate(pcount=Count('products'))
    return render(request, 'dashboard/materials.html', {
        'active': 'materials', 'materials': materials,
    })


@staff_member_required
def material_create(request):
    return _form_view(
        request, MaterialForm, None, active='materials',
        title='Yangi material', subtitle='Material nomi',
        list_url='dashboard:materials', redirect_url='dashboard:materials',
        msg="Material qo'shildi.",
    )


@staff_member_required
def material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk)
    return _form_view(
        request, MaterialForm, material, active='materials',
        title=material.name, subtitle='Materialni tahrirlash',
        list_url='dashboard:materials', redirect_url='dashboard:materials',
        msg='Material yangilandi.',
    )


@staff_member_required
def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk)
    return _delete_view(request, material, redirect_url='dashboard:materials', label=f'"{material.name}"')


# =============================================================
#  XONA TURLARI
# =============================================================
@staff_member_required
def roomtypes_list(request):
    room_types = RoomType.objects.annotate(pcount=Count('products'))
    return render(request, 'dashboard/roomtypes.html', {
        'active': 'roomtypes', 'room_types': room_types,
    })


@staff_member_required
def roomtype_create(request):
    return _form_view(
        request, RoomTypeForm, None, active='roomtypes',
        title='Yangi xona turi', subtitle='Xona turi nomi',
        list_url='dashboard:roomtypes', redirect_url='dashboard:roomtypes',
        msg="Xona turi qo'shildi.",
    )


@staff_member_required
def roomtype_edit(request, pk):
    room_type = get_object_or_404(RoomType, pk=pk)
    return _form_view(
        request, RoomTypeForm, room_type, active='roomtypes',
        title=room_type.name, subtitle='Xona turini tahrirlash',
        list_url='dashboard:roomtypes', redirect_url='dashboard:roomtypes',
        msg='Xona turi yangilandi.',
    )


@staff_member_required
def roomtype_delete(request, pk):
    room_type = get_object_or_404(RoomType, pk=pk)
    return _delete_view(request, room_type, redirect_url='dashboard:roomtypes', label=f'"{room_type.name}"')


# =============================================================
#  BANNERLAR
# =============================================================
@staff_member_required
def banners_list(request):
    banners = Banner.objects.all()
    return render(request, 'dashboard/banners.html', {
        'active': 'banners', 'banners': banners,
    })


@staff_member_required
def banner_create(request):
    return _form_view(
        request, BannerForm, None, active='banners',
        title='Yangi banner', subtitle='Bosh sahifa slayderi',
        list_url='dashboard:banners', redirect_url='dashboard:banners',
        msg="Banner qo'shildi.",
    )


@staff_member_required
def banner_edit(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    return _form_view(
        request, BannerForm, banner, active='banners',
        title=banner.title, subtitle='Bannerni tahrirlash',
        list_url='dashboard:banners', redirect_url='dashboard:banners',
        msg='Banner yangilandi.',
    )


@staff_member_required
def banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    return _delete_view(request, banner, redirect_url='dashboard:banners', label=f'"{banner.title}"')


# =============================================================
#  PROMOKODLAR
# =============================================================
@staff_member_required
def promocodes_list(request):
    promocodes = PromoCode.objects.all()
    return render(request, 'dashboard/promocodes.html', {
        'active': 'promocodes', 'promocodes': promocodes,
    })


@staff_member_required
def promocode_create(request):
    return _form_view(
        request, PromoCodeForm, None, active='promocodes',
        title='Yangi promokod', subtitle='Chegirma kodi',
        list_url='dashboard:promocodes', redirect_url='dashboard:promocodes',
        msg="Promokod qo'shildi.",
    )


@staff_member_required
def promocode_edit(request, pk):
    promocode = get_object_or_404(PromoCode, pk=pk)
    return _form_view(
        request, PromoCodeForm, promocode, active='promocodes',
        title=promocode.code, subtitle='Promokodni tahrirlash',
        list_url='dashboard:promocodes', redirect_url='dashboard:promocodes',
        msg='Promokod yangilandi.',
    )


@staff_member_required
def promocode_delete(request, pk):
    promocode = get_object_or_404(PromoCode, pk=pk)
    return _delete_view(request, promocode, redirect_url='dashboard:promocodes', label=f'"{promocode.code}"')


# =============================================================
#  MIJOZLAR / FOYDALANUVCHILAR
# =============================================================
@staff_member_required
def customers_list(request):
    role = request.GET.get('role', 'customer')
    users = User.objects.annotate(
        orders_count=Count('orders', distinct=True),
        spent=Coalesce(
            Sum('orders__total_price', filter=~Q(orders__status=Order.STATUS_CANCELLED)),
            Decimal(0),
            output_field=DecimalField(),
        ),
    ).order_by('-date_joined')

    if role == 'staff':
        users = users.filter(is_staff=True)
    else:
        users = users.filter(is_staff=False)

    query = request.GET.get('q', '').strip()
    if query:
        users = users.filter(Q(full_name__icontains=query) | Q(phone_number__icontains=query))

    return render(request, 'dashboard/customers.html', {
        'active': 'customers', 'customers': users, 'query': query, 'role': role,
    })


@staff_member_required
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Foydalanuvchi "{user.get_short_name()}" qo\'shildi.')
            return redirect('dashboard:customers')
    else:
        form = UserCreateForm()
    return render(request, 'dashboard/generic_form.html', {
        'active': 'customers', 'form': form, 'form_title': 'Yangi foydalanuvchi',
        'form_subtitle': "Mijoz yoki xodim qo'shish", 'list_url': 'dashboard:customers',
    })


@staff_member_required
def user_edit(request, pk):
    edit_user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=edit_user)
        formset = AddressFormSet(request.POST, instance=edit_user, prefix='addr')
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Foydalanuvchi yangilandi.')
            return redirect('dashboard:customers')
    else:
        form = UserEditForm(instance=edit_user)
        formset = AddressFormSet(instance=edit_user, prefix='addr')
    return render(request, 'dashboard/user_form.html', {
        'active': 'customers', 'form': form, 'address_formset': formset,
        'title': edit_user.get_short_name(), 'edit_user': edit_user,
    })


@staff_member_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, "O'zingizni o'chira olmaysiz.")
        else:
            name = user.get_short_name()
            user.delete()
            messages.success(request, f'Foydalanuvchi "{name}" o\'chirildi.')
    return redirect('dashboard:customers')


# =============================================================
#  SEVIMLILAR (faqat ko'rish)
# =============================================================
@staff_member_required
def wishlist_list(request):
    items = WishlistItem.objects.select_related('user', 'product').order_by('-created_at')
    return render(request, 'dashboard/wishlist.html', {
        'active': 'wishlist', 'items': items,
    })
