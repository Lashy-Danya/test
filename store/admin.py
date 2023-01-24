from django.contrib import admin

from .models import (
    Category, Manufacturer, Product, ProductImage,
    ProductTechnicalData, ProductTechnicalDataValue, ProductType, Discount
)

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['amount', 'reason']

@admin.register(Category)
class CatygoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug',]
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'country',]

class ProductTechnicalDataInline(admin.TabularInline):
    model = ProductTechnicalData

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [ProductTechnicalDataInline,]

class ProductImageInline(admin.TabularInline):
    model = ProductImage

class ProductTechnicalDataValueInline(admin.TabularInline):
    model = ProductTechnicalDataValue

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Модель Продукта в админ панеле"""
    list_display = ['name', 'category', 'product_type', 'price', 'warranty', 'is_active', 'count']
    list_filter = ['is_active',]
    inlines = [ProductTechnicalDataValueInline, ProductImageInline,]