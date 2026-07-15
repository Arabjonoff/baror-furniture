from django import forms

from accounts.models import phone_validator

from .models import Order


class AddressSelectWidget(forms.Select):
    """Saqlangan manzil tanlanganda formani JS orqali avtomatik to'ldirish uchun data-atributlar."""

    def __init__(self, addresses=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addresses = {str(address.pk): address for address in (addresses or [])}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        address = self.addresses.get(str(value))
        if address:
            option['attrs']['data-region'] = address.region
            option['attrs']['data-district'] = address.district
            option['attrs']['data-street'] = address.street
        return option


class CheckoutForm(forms.Form):
    """Buyurtma berish formasi — savatdan checkout jarayoni uchun."""

    full_name = forms.CharField(label='Ism', max_length=150)
    phone = forms.CharField(
        label='Telefon',
        max_length=13,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'placeholder': '+998901234567'}),
    )
    region = forms.CharField(label='Viloyat', max_length=100)
    district = forms.CharField(label='Tuman', max_length=100)
    address = forms.CharField(label="Ko'cha, uy", max_length=255)
    delivery_type = forms.ChoiceField(label='Yetkazib berish turi', choices=Order.DELIVERY_TYPE_CHOICES)
    comment = forms.CharField(label='Izoh', required=False, widget=forms.Textarea(attrs={'rows': 3}))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None and user.is_authenticated:
            addresses = list(user.addresses.all())
            if addresses:
                self.fields['saved_address'] = forms.ModelChoiceField(
                    queryset=user.addresses.all(),
                    required=False,
                    label='Saqlangan manzildan tanlang',
                    widget=AddressSelectWidget(addresses=addresses),
                )
                self.order_fields(
                    ['saved_address', 'full_name', 'phone', 'region', 'district', 'address', 'delivery_type', 'comment']
                )
