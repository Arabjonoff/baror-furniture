from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('buyurtmalar/', views.orders_list, name='orders'),
    path('buyurtmalar/<int:order_id>/', views.order_detail, name='order_detail'),
    path('mahsulotlar/', views.products_list, name='products'),
    path('mahsulotlar/yangi/', views.product_create, name='product_create'),
    path('mahsulotlar/<int:product_id>/tahrirlash/', views.product_edit, name='product_edit'),
    path('mahsulotlar/<int:product_id>/ochirish/', views.product_delete, name='product_delete'),
    path('mijozlar/', views.customers_list, name='customers'),
]
