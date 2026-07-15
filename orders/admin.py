from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'color', 'price', 'quantity', 'cost')
    readonly_fields = ('product', 'color', 'price', 'quantity', 'cost')

    def has_add_permission(self, request, obj=None):
        return False

    def cost(self, obj):
        return obj.get_cost()
    cost.short_description = 'Jami'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'full_name', 'phone', 'total_price', 'status', 'payment_status',
        'payment_method', 'delivery_type', 'created_at',
    )
    list_display_links = ('id', 'full_name')
    list_editable = ('status', 'payment_status')
    list_filter = ('status', 'payment_status', 'payment_method', 'delivery_type', 'created_at')
    search_fields = ('id', 'full_name', 'phone')
    date_hierarchy = 'created_at'
    readonly_fields = ('total_price', 'created_at')
    inlines = [OrderItemInline]
