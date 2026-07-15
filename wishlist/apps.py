from django.apps import AppConfig


class WishlistConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wishlist'
    verbose_name = 'Sevimlilar'

    def ready(self):
        from . import signals  # noqa: F401 — login signalini ulaydi
