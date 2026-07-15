from decimal import Decimal

from catalog.models import Product

CART_SESSION_ID = 'cart'


class Cart:
    """Session asosidagi savat — ro'yxatdan o'tmagan foydalanuvchilar uchun ham ishlaydi."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if cart is None:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    @staticmethod
    def _make_key(product_id, color=None):
        return f'{product_id}:{color}' if color else str(product_id)

    def save(self):
        self.session.modified = True

    def add(self, product, quantity=1, color='', update_quantity=False):
        """Mahsulotni savatga qo'shadi. update_quantity=True bo'lsa miqdorni almashtiradi, aks holda qo'shadi."""
        key = self._make_key(product.id, color)
        if key not in self.cart:
            self.cart[key] = {
                'product_id': product.id,
                'quantity': 0,
                'price': str(product.price),
                'color': color or '',
            }

        if update_quantity:
            self.cart[key]['quantity'] = quantity
        else:
            self.cart[key]['quantity'] += quantity

        max_quantity = product.stock or 1
        self.cart[key]['quantity'] = max(1, min(self.cart[key]['quantity'], max_quantity))
        self.save()

    def remove(self, product, color=''):
        key = self._make_key(product.id, color)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def update(self, product, quantity, color=''):
        key = self._make_key(product.id, color)
        if key in self.cart:
            max_quantity = product.stock or 1
            self.cart[key]['quantity'] = max(1, min(quantity, max_quantity))
            self.save()

    def clear(self):
        self.session[CART_SESSION_ID] = {}
        self.save()

    def __iter__(self):
        product_ids = [item['product_id'] for item in self.cart.values()]
        products_map = Product.objects.in_bulk(product_ids)

        for key, item in self.cart.items():
            product = products_map.get(item['product_id'])
            if not product:
                continue
            data = item.copy()
            data['key'] = key
            data['product'] = product
            data['price'] = Decimal(item['price'])
            data['total_price'] = data['price'] * data['quantity']
            yield data

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
