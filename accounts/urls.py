from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('royxatdan-otish/', views.register_view, name='register'),
    path('kirish/', views.login_view, name='login'),
    path('chiqish/', views.logout_view, name='logout'),
    path('profil/', views.profile_view, name='profile'),
    path('parol/', views.password_change_view, name='password_change'),
    path('manzil/qoshish/', views.address_add_view, name='address_add'),
    path('manzil/<int:address_id>/tahrirlash/', views.address_edit_view, name='address_edit'),
    path('manzil/<int:address_id>/ochirish/', views.address_delete_view, name='address_delete'),
]
