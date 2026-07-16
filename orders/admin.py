from django.contrib import admin

from .models import Order, OrderItem, PromoCode


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
    readonly_fields = ('total_price', 'discount', 'promo_code', 'created_at')
    inlines = [OrderItemInline]


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'discount_type', 'discount_value', 'min_order_amount',
        'used_count', 'usage_limit', 'valid_until', 'is_active',
    )
    list_editable = ('is_active',)
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code', 'description')
    readonly_fields = ('used_count', 'created_at')
    fieldsets = (
        (None, {'fields': ('code', 'description', 'is_active')}),
        ('Chegirma', {'fields': ('discount_type', 'discount_value', 'max_discount', 'min_order_amount')}),
        ('Amal muddati va limit', {'fields': ('valid_from', 'valid_until', 'usage_limit', 'used_count')}),
        ('Boshqa', {'fields': ('created_at',)}),
    )
