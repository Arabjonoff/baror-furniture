from .cart import Cart


def cart(request):
    """Savatni har bir shablonda mavjud qiladi.

    - ``cart`` — savat obyekti (header'dagi son uchun)
    - ``cart_quantities`` — {product_id: miqdor} rangsiz yozuvlar bo'yicha
      (mahsulot kartochkasidagi +/- stepper boshlang'ich holati uchun)
    """
    c = Cart(request)
    quantities = {}
    for key, item in c.cart.items():
        # Kartochka rang tanlamaydi — faqat rangsiz (":" belgisisiz) yozuvlar
        if ':' not in key:
            quantities[item['product_id']] = item['quantity']
    return {'cart': c, 'cart_quantities': quantities}
