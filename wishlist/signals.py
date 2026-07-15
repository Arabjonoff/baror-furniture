from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .wishlist import Wishlist


@receiver(user_logged_in)
def merge_wishlist_on_login(sender, request, user, **kwargs):
    """Mehmon sifatida belgilangan sevimlilar login qilganda bazaga ko'chadi."""
    Wishlist.merge_session_to_user(request, user)
