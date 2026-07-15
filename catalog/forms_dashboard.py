from django import forms

from .models import Product


class ProductDashboardForm(forms.ModelForm):
    """Boshqaruv panelida mahsulot qo'shish/tahrirlash formasi."""

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'description', 'price', 'old_price',
            'material', 'room_type', 'width', 'height', 'depth', 'weight',
            'stock', 'is_available', 'is_featured',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
