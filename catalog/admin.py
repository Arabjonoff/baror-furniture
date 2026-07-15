from django.contrib import admin
from django.utils.html import format_html

from .models import Banner, Category, Material, Product, ProductColor, ProductImage, RoomType

admin.site.site_header = 'Barormebel boshqaruv paneli'
admin.site.site_title = 'Barormebel Admin'
admin.site.index_title = 'Boshqaruv paneli'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'preview', 'is_main', 'order')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:4px;object-fit:cover;" />', obj.image.url)
        return '—'
    preview.short_description = "Ko'rinish"


class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    fields = ('color_name', 'color_hex', 'swatch', 'image')
    readonly_fields = ('swatch',)

    def swatch(self, obj):
        if obj.color_hex:
            return format_html(
                '<span style="display:inline-block;width:24px;height:24px;border-radius:50%;'
                'background:{};border:1px solid #ccc;"></span>',
                obj.color_hex,
            )
        return '—'
    swatch.short_description = 'Rang'


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'image_preview')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;object-fit:cover;" />', obj.image.url)
        return '—'
    image_preview.short_description = 'Rasm'


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Mahsulotlar soni'


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Mahsulotlar soni'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'image_preview')
    list_filter = ('is_active', 'parent')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;object-fit:cover;" />', obj.image.url)
        return '—'
    image_preview.short_description = 'Rasm'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'price', 'stock', 'is_available', 'is_featured', 'image_preview',
    )
    list_filter = ('category', 'material', 'room_type', 'is_available', 'is_featured')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock')
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    inlines = [ProductImageInline, ProductColorInline]

    def image_preview(self, obj):
        main_image = obj.images.first()
        if main_image:
            return format_html('<img src="{}" style="height:50px;border-radius:4px;object-fit:cover;" />', main_image.image.url)
        return '—'
    image_preview.short_description = 'Rasm'
