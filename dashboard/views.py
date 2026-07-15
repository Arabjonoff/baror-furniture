from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, DecimalField, Q, Sum
from django.db.models.functions import Coalesce, TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User
from catalog.forms_dashboard import ProductDashboardForm
from catalog.models import Category, Product
from orders.models import Order

LOW_STOCK_THRESHOLD = 5


def _money(value):
    return Decimal(value or 0)


@staff_member_required
def index(request):
    """Boshqaruv paneli bosh sahifasi — asosiy statistikalar va grafiklar."""
    orders = Order.objects.all()
    active_orders = orders.exclude(status=Order.STATUS_CANCELLED)

    total_revenue = active_orders.aggregate(
        s=Coalesce(Sum('total_price'), Decimal(0), output_field=DecimalField())
    )['s']

    # Asosiy raqamlar
    stats = {
        'revenue': total_revenue,
        'orders_total': orders.count(),
        'orders_new': orders.filter(status=Order.STATUS_NEW).count(),
        'products_total': Product.objects.count(),
        'low_stock': Product.objects.filter(stock__lte=LOW_STOCK_THRESHOLD).count(),
        'customers': User.objects.filter(is_staff=False).count(),
    }

    # Oxirgi 7 kunlik daromad grafigi
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

    # Holat bo'yicha taqsimot
    status_counts = {row['status']: row['c'] for row in orders.values('status').annotate(c=Count('id'))}
    status_breakdown = [
        {'code': code, 'label': label, 'count': status_counts.get(code, 0)}
        for code, label in Order.STATUS_CHOICES
    ]

    # Eng ko'p sotilgan mahsulotlar
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


@staff_member_required
def orders_list(request):
    """Buyurtmalar ro'yxati — holat bo'yicha filtr bilan."""
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
    """Buyurtma tafsilotlari va holatni yangilash."""
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
def products_list(request):
    """Mahsulotlar ro'yxati — qidiruv va kategoriya filtri bilan."""
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


@staff_member_required
def product_create(request):
    """Yangi mahsulot qo'shish."""
    if request.method == 'POST':
        form = ProductDashboardForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'"{product.name}" qo\'shildi.')
            return redirect('dashboard:products')
    else:
        form = ProductDashboardForm()
    return render(request, 'dashboard/product_form.html', {
        'active': 'products', 'form': form, 'title': "Yangi mahsulot",
    })


@staff_member_required
def product_edit(request, product_id):
    """Mahsulotni tahrirlash."""
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductDashboardForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mahsulot yangilandi.')
            return redirect('dashboard:products')
    else:
        form = ProductDashboardForm(instance=product)
    return render(request, 'dashboard/product_form.html', {
        'active': 'products', 'form': form, 'title': product.name, 'product': product,
    })


@staff_member_required
def product_delete(request, product_id):
    """Mahsulotni o'chirish."""
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'"{name}" o\'chirildi.')
    return redirect('dashboard:products')


@staff_member_required
def customers_list(request):
    """Mijozlar ro'yxati — buyurtmalar soni bilan."""
    customers = (
        User.objects.filter(is_staff=False)
        .annotate(
            orders_count=Count('orders', distinct=True),
            spent=Coalesce(
                Sum('orders__total_price', filter=~Q(orders__status=Order.STATUS_CANCELLED)),
                Decimal(0),
                output_field=DecimalField(),
            ),
        )
        .order_by('-date_joined')
    )
    query = request.GET.get('q', '').strip()
    if query:
        customers = customers.filter(Q(full_name__icontains=query) | Q(phone_number__icontains=query))

    return render(request, 'dashboard/customers.html', {
        'active': 'customers', 'customers': customers, 'query': query,
    })
