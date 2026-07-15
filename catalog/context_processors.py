from .models import Category


def categories(request):
    """Header va footer menyularida ko'rsatiladigan asosiy kategoriyalar ro'yxati."""
    return {
        'nav_categories': Category.objects.filter(is_active=True, parent__isnull=True).order_by('name'),
    }
