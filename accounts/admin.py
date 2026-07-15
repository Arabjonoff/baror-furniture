from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Address, User


class UserCreationFormCustom(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('phone_number', 'full_name')


class UserChangeFormCustom(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationFormCustom
    form = UserChangeFormCustom
    model = User
    list_display = ('phone_number', 'full_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('phone_number', 'full_name')
    ordering = ('-date_joined',)
    inlines = [AddressInline]

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ("Shaxsiy ma'lumotlar", {'fields': ('full_name', 'email', 'avatar', 'birth_date', 'gender')}),
        ('Sodiqlik va bildirishnomalar', {'fields': ('bonus_points', 'notify_sms', 'notify_email')}),
        ('Ruxsatlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Muhim sanalar', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'password1', 'password2'),
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'region', 'district', 'is_default')
    list_filter = ('region', 'is_default')
    search_fields = ('user__phone_number', 'user__full_name', 'region', 'district')
