"""Boshqaruv paneli (dashboard) uchun barcha ModelForm va formsetlar.

Django admin'dagi bo'limlarni maxsus panelga ko'chirish uchun ishlatiladi.
"""
from django import forms
from django.forms import inlineformset_factory

from accounts.models import Address, User
from catalog.models import Banner, Category, Material, Product, ProductColor, ProductImage, RoomType
from orders.models import PromoCode


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent', 'image', 'is_active']


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name']


class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = ['name']


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = [
            'eyebrow', 'title', 'description', 'image',
            'button_text', 'button_link', 'order', 'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class PromoCodeForm(forms.ModelForm):
    class Meta:
        model = PromoCode
        fields = [
            'code', 'description', 'discount_type', 'discount_value',
            'max_discount', 'min_order_amount', 'valid_from', 'valid_until',
            'usage_limit', 'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'valid_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('valid_from', 'valid_until'):
            self.fields[name].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']


class ProductForm(forms.ModelForm):
    """Mahsulot asosiy ma'lumotlari (rasm/ranglar alohida formsetlarda)."""

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


# Mahsulot rasmlari va ranglari — inline formsetlar (dashboardda to'g'ridan-to'g'ri boshqariladi)
ProductImageFormSet = inlineformset_factory(
    Product, ProductImage,
    fields=['image', 'is_main', 'order'],
    extra=2, can_delete=True,
)

class ProductColorForm(forms.ModelForm):
    class Meta:
        model = ProductColor
        fields = ['color_name', 'color_hex', 'image']
        widgets = {'color_hex': forms.TextInput(attrs={'type': 'color'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # type=color har doim '#000000' yuboradi — bo'sh qatorlar "o'zgargan"dek
        # hisoblanmasligi uchun initial ni ham shu qiymatga tenglaymiz.
        self.fields['color_hex'].initial = '#000000'


ProductColorFormSet = inlineformset_factory(
    Product, ProductColor,
    form=ProductColorForm,
    extra=1, can_delete=True,
)


class UserCreateForm(forms.ModelForm):
    """Yangi foydalanuvchi (mijoz yoki xodim) qo'shish — parol bilan."""

    password = forms.CharField(
        label='Parol', widget=forms.PasswordInput, min_length=4,
        help_text="Kamida 4 belgi.",
    )

    class Meta:
        model = User
        fields = ['phone_number', 'full_name', 'email', 'is_active', 'is_staff']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    """Foydalanuvchini tahrirlash — parol ixtiyoriy (bo'sh qoldirilsa o'zgarmaydi)."""

    new_password = forms.CharField(
        label='Yangi parol', widget=forms.PasswordInput, required=False, min_length=4,
        help_text="O'zgartirmaslik uchun bo'sh qoldiring.",
    )

    class Meta:
        model = User
        fields = [
            'phone_number', 'full_name', 'email', 'avatar', 'birth_date', 'gender',
            'bonus_points', 'notify_sms', 'notify_email', 'is_active', 'is_staff',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['birth_date'].input_formats = ['%Y-%m-%d']

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get('new_password')
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
        return user


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['region', 'district', 'street', 'landmark', 'phone_number', 'is_default']


AddressFormSet = inlineformset_factory(
    User, Address,
    form=AddressForm,
    extra=1, can_delete=True,
)
