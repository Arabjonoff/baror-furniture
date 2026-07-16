from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='detail'),
    path('qoshish/<int:product_id>/', views.cart_add, name='add'),
    path('ochirish/<int:product_id>/', views.cart_remove, name='remove'),
    path('yangilash/<int:product_id>/', views.cart_update, name='update'),
    path('promokod/', views.cart_apply_promo, name='apply_promo'),
    path('promokod/olib-tashlash/', views.cart_remove_promo, name='remove_promo'),
]
