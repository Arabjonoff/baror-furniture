from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Product

from .forms import AddressForm, PhoneLoginForm, ProfileForm, RegisterForm
from .models import Address


def register_view(request):
    """Telefon raqami va parol orqali ro'yxatdan o'tish."""
    if request.user.is_authenticated:
        return redirect('catalog:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz!")
            return redirect('catalog:home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Telefon raqami orqali tizimga kirish."""
    if request.user.is_authenticated:
        return redirect('catalog:home')

    if request.method == 'POST':
        form = PhoneLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Xush kelibsiz!')
            next_url = request.POST.get('next') or request.GET.get('next')
            return redirect(next_url or 'catalog:home')
    else:
        form = PhoneLoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Tizimdan chiqish."""
    logout(request)
    messages.success(request, 'Tizimdan chiqdingiz.')
    return redirect('catalog:home')


@login_required
def profile_view(request):
    """Profil sahifasi — shaxsiy ma'lumotlar, manzillar va buyurtmalar tarixi."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ma\'lumotlar yangilandi.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)

    addresses = request.user.addresses.all()

    # Ko'rilgan mahsulotlar (sessiyadagi tartibni saqlab)
    viewed_ids = request.session.get('recently_viewed', [])
    recently_viewed = []
    if viewed_ids:
        products = Product.objects.filter(pk__in=viewed_ids, is_available=True).select_related('category')
        products_by_id = {p.pk: p for p in products}
        recently_viewed = [products_by_id[pid] for pid in viewed_ids if pid in products_by_id]

    context = {
        'form': form,
        'addresses': addresses,
        'orders_count': request.user.orders.count(),
        'addresses_count': addresses.count(),
        'recently_viewed': recently_viewed,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def password_change_view(request):
    """Parolni o'zgartirish."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Parol muvaffaqiyatli o'zgartirildi.")
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/password_change.html', {'form': form})


@login_required
def address_add_view(request):
    """Yangi manzil qo'shish."""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Manzil qo'shildi.")
            return redirect('accounts:profile')
    else:
        form = AddressForm()

    return render(request, 'accounts/address_form.html', {'form': form, 'title': "Manzil qo'shish"})


@login_required
def address_edit_view(request, address_id):
    """Mavjud manzilni tahrirlash."""
    address = get_object_or_404(Address, pk=address_id, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Manzil yangilandi.')
            return redirect('accounts:profile')
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Manzilni tahrirlash'})


@login_required
def address_delete_view(request, address_id):
    """Manzilni o'chirish."""
    address = get_object_or_404(Address, pk=address_id, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, "Manzil o'chirildi.")
    return redirect('accounts:profile')
