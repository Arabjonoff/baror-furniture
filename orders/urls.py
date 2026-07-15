from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list_view, name='list'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('tasdiqlash/<int:order_id>/', views.order_confirmation_view, name='confirmation'),
    path('<int:order_id>/', views.order_detail_view, name='detail'),
]
