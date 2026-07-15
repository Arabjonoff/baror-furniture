from orders.models import Order


def dashboard_badges(request):
    """Yon menyudagi yangi buyurtmalar sonini beradi (faqat dashboard sahifalarida)."""
    if request.path.startswith('/boshqaruv/') and request.user.is_authenticated and request.user.is_staff:
        return {'new_orders_count': Order.objects.filter(status=Order.STATUS_NEW).count()}
    return {}
