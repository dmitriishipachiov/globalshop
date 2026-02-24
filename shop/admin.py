from django.contrib import admin

from .models import *

@admin.register(CategoryShop)
class CategoryShopAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('title',)}


@admin.register(SubcategoryShop)
class SubcategoryShopAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('title',)}


@admin.register(ProductShop)
class ProductShopAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('title',)}
    list_display = ('title', 'price', 'quantity', 'discount', 'is_bestseller', 'is_promo')
    list_editable = ('is_bestseller', 'is_promo', 'quantity', 'price', 'discount')
    search_fields = ['title']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('image',)}
