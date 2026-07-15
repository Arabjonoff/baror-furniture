from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, render

from .models import Banner, Category, Material, Product, ProductColor, RoomType

PRODUCTS_PER_PAGE = 12

SORT_OPTIONS = {
    'narx_osish': 'price',
    'narx_kamayish': '-price',
    'yangi': '-created_at',
    'ommabop': '-views_count',
}


def home(request):
    """Bosh sahifa — tanlangan mahsulotlar va kategoriyalar ro'yxati."""
    featured_products = (
        Product.objects.filter(is_available=True, is_featured=True)
        .select_related('category')
        .order_by('-created_at')[:8]
    )
    categories = Category.objects.filter(is_active=True, parent__isnull=True)
    banners = Banner.objects.filter(is_active=True)
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'banners': banners,
    }
    return render(request, 'catalog/home.html', context)


def _parse_decimal(value):
    """GET parametridan Decimal olishga urinadi, xato bo'lsa None qaytaradi."""
    if not value:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def product_list(request, category_slug=None):
    """Mahsulotlar ro'yxati — kategoriya bo'yicha, filtr, qidiruv va saralash bilan."""
    category = None
    products = Product.objects.select_related('category')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    price_min = _parse_decimal(request.GET.get('price_min'))
    if price_min is not None:
        products = products.filter(price__gte=price_min)

    price_max = _parse_decimal(request.GET.get('price_max'))
    if price_max is not None:
        products = products.filter(price__lte=price_max)

    material = request.GET.get('material', '')
    if material:
        products = products.filter(material__slug=material)

    room_type = request.GET.get('room_type', '')
    if room_type:
        products = products.filter(room_type__slug=room_type)

    color = request.GET.get('color', '')
    if color:
        products = products.filter(colors__color_name__iexact=color)

    available_only = request.GET.get('available') == '1'
    if available_only:
        products = products.filter(is_available=True, stock__gt=0)

    sort = request.GET.get('sort', 'yangi')
    products = products.order_by(SORT_OPTIONS.get(sort, '-created_at')).distinct()

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'category': category,
        'categories': Category.objects.filter(is_active=True),
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'materials': Material.objects.all(),
        'room_types': RoomType.objects.all(),
        'colors': ProductColor.objects.values_list('color_name', flat=True).distinct().order_by('color_name'),
        'query': query,
        'selected_sort': sort,
        'selected_material': material,
        'selected_room_type': room_type,
        'selected_color': color,
        'price_min': request.GET.get('price_min', ''),
        'price_max': request.GET.get('price_max', ''),
        'available_only': available_only,
    }
    return render(request, 'catalog/product_list.html', context)


def product_detail(request, slug):
    """Mahsulot detali — galereya, ranglar, o'lchamlar va o'xshash mahsulotlar."""
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images', 'colors'),
        slug=slug,
    )

    Product.objects.filter(pk=product.pk).update(views_count=F('views_count') + 1)
    product.views_count += 1

    # Ko'rilgan mahsulotlar tarixi (sessiyada, eng oxirgisi birinchi, 12 tagacha)
    viewed = request.session.get('recently_viewed', [])
    if product.pk in viewed:
        viewed.remove(product.pk)
    viewed.insert(0, product.pk)
    request.session['recently_viewed'] = viewed[:12]

    # O'xshash mahsulotlar: avval o'sha kategoriya, yetmasa o'sha xona turi/material,
    # u ham yetmasa boshqa mavjud mahsulotlar bilan to'ldiramiz (4 tagacha).
    SIMILAR_LIMIT = 4
    similar_products = list(
        Product.objects.filter(category=product.category, is_available=True)
        .exclude(pk=product.pk)
        .select_related('category')[:SIMILAR_LIMIT]
    )

    if len(similar_products) < SIMILAR_LIMIT:
        picked_ids = [product.pk] + [p.pk for p in similar_products]
        tag_filter = Q()
        if product.room_type_id:
            tag_filter |= Q(room_type=product.room_type)
        if product.material_id:
            tag_filter |= Q(material=product.material)
        if tag_filter:
            similar_products += list(
                Product.objects.filter(tag_filter, is_available=True)
                .exclude(pk__in=picked_ids)
                .select_related('category')[:SIMILAR_LIMIT - len(similar_products)]
            )

    if len(similar_products) < SIMILAR_LIMIT:
        picked_ids = [product.pk] + [p.pk for p in similar_products]
        similar_products += list(
            Product.objects.filter(is_available=True)
            .exclude(pk__in=picked_ids)
            .select_related('category')
            .order_by('-created_at')[:SIMILAR_LIMIT - len(similar_products)]
        )

    context = {
        'product': product,
        'similar_products': similar_products,
    }
    return render(request, 'catalog/product_detail.html', context)
