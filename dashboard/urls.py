from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),

    # Buyurtmalar
    path('buyurtmalar/', views.orders_list, name='orders'),
    path('buyurtmalar/<int:order_id>/', views.order_detail, name='order_detail'),
    path('buyurtmalar/<int:order_id>/ochirish/', views.order_delete, name='order_delete'),

    # Mahsulotlar
    path('mahsulotlar/', views.products_list, name='products'),
    path('mahsulotlar/yangi/', views.product_create, name='product_create'),
    path('mahsulotlar/<int:product_id>/tahrirlash/', views.product_edit, name='product_edit'),
    path('mahsulotlar/<int:product_id>/ochirish/', views.product_delete, name='product_delete'),

    # Kategoriyalar
    path('kategoriyalar/', views.categories_list, name='categories'),
    path('kategoriyalar/yangi/', views.category_create, name='category_create'),
    path('kategoriyalar/<int:pk>/tahrirlash/', views.category_edit, name='category_edit'),
    path('kategoriyalar/<int:pk>/ochirish/', views.category_delete, name='category_delete'),

    # Materiallar
    path('materiallar/', views.materials_list, name='materials'),
    path('materiallar/yangi/', views.material_create, name='material_create'),
    path('materiallar/<int:pk>/tahrirlash/', views.material_edit, name='material_edit'),
    path('materiallar/<int:pk>/ochirish/', views.material_delete, name='material_delete'),

    # Xona turlari
    path('xona-turlari/', views.roomtypes_list, name='roomtypes'),
    path('xona-turlari/yangi/', views.roomtype_create, name='roomtype_create'),
    path('xona-turlari/<int:pk>/tahrirlash/', views.roomtype_edit, name='roomtype_edit'),
    path('xona-turlari/<int:pk>/ochirish/', views.roomtype_delete, name='roomtype_delete'),

    # Bannerlar
    path('bannerlar/', views.banners_list, name='banners'),
    path('bannerlar/yangi/', views.banner_create, name='banner_create'),
    path('bannerlar/<int:pk>/tahrirlash/', views.banner_edit, name='banner_edit'),
    path('bannerlar/<int:pk>/ochirish/', views.banner_delete, name='banner_delete'),

    # Promokodlar
    path('promokodlar/', views.promocodes_list, name='promocodes'),
    path('promokodlar/yangi/', views.promocode_create, name='promocode_create'),
    path('promokodlar/<int:pk>/tahrirlash/', views.promocode_edit, name='promocode_edit'),
    path('promokodlar/<int:pk>/ochirish/', views.promocode_delete, name='promocode_delete'),

    # Mijozlar / foydalanuvchilar
    path('mijozlar/', views.customers_list, name='customers'),
    path('mijozlar/yangi/', views.user_create, name='user_create'),
    path('mijozlar/<int:pk>/tahrirlash/', views.user_edit, name='user_edit'),
    path('mijozlar/<int:pk>/ochirish/', views.user_delete, name='user_delete'),

    # Sevimlilar
    path('sevimlilar/', views.wishlist_list, name='wishlist'),
]
