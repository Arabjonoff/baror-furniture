from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Address, User, phone_validator


class RegisterForm(forms.Form):
    """Telefon raqami va parol orqali ro'yxatdan o'tish formasi."""

    phone_number = forms.CharField(
        label='Telefon raqami',
        max_length=13,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'placeholder': '+998901234567'}),
    )
    full_name = forms.CharField(label='Ism', max_length=150)
    password1 = forms.CharField(label='Parol', widget=forms.PasswordInput, min_length=6)
    password2 = forms.CharField(label="Parolni tasdiqlang", widget=forms.PasswordInput, min_length=6)

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('Bu telefon raqami allaqachon ro\'yxatdan o\'tgan.')
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Parollar mos kelmadi.')
        return cleaned_data

    def save(self):
        return User.objects.create_user(
            phone_number=self.cleaned_data['phone_number'],
            password=self.cleaned_data['password1'],
            full_name=self.cleaned_data['full_name'],
        )


class PhoneLoginForm(AuthenticationForm):
    """Standart AuthenticationForm — faqat maydon nomlarini telefon raqamiga moslashtiradi."""

    username = forms.CharField(label='Telefon raqami', widget=forms.TextInput(attrs={'placeholder': '+998901234567'}))
    password = forms.CharField(label='Parol', widget=forms.PasswordInput)

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': "Telefon raqami yoki parol noto'g'ri.",
    }


class ProfileForm(forms.ModelForm):
    """Foydalanuvchi shaxsiy ma'lumotlarini o'zgartirish formasi."""

    class Meta:
        model = User
        fields = ['avatar', 'full_name', 'email', 'birth_date', 'gender', 'notify_sms', 'notify_email']
        labels = {
            'avatar': 'Profil rasmi',
            'full_name': 'Ism',
            'email': 'Email',
            'birth_date': "Tug'ilgan sana",
            'gender': 'Jinsi',
            'notify_sms': 'SMS orqali aksiya va yangiliklar',
            'notify_email': 'Email orqali aksiya va yangiliklar',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Ism familiyangiz'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@example.com'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }


class AddressForm(forms.ModelForm):
    """Yetkazib berish manzilini qo'shish/tahrirlash formasi."""

    class Meta:
        model = Address
        fields = ['region', 'district', 'street', 'landmark', 'phone_number', 'is_default']
        labels = {
            'region': 'Viloyat',
            'district': 'Tuman',
            'street': "Ko'cha, uy",
            'landmark': "Mo'ljal",
            'phone_number': 'Aloqa uchun telefon',
            'is_default': 'Asosiy manzil sifatida belgilash',
        }
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': '+998901234567'}),
        }
