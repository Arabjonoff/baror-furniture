from .cart import Cart


def cart(request):
    """Savatni har bir shablonda ({{ cart }}) mavjud qiladi — header'dagi son uchun."""
    return {'cart': Cart(request)}
