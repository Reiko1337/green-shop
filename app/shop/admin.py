from django.contrib import admin
from . import models
from django import forms
from .utils import CartProductFilterFKPAdmin


class CountProductValidation(forms.ModelForm):
    def clean_qty(self):
        qty = self.cleaned_data.get('qty')
        product = self.cleaned_data.get('product')
        if product.qty < qty:
            raise forms.ValidationError('Такого количества нет в наличии')
        return qty


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')


class CartProductAdmin(CartProductFilterFKPAdmin, admin.ModelAdmin):
    readonly_fields = ('final_price',)
    list_display = ('id','customer', 'product', 'cart', 'qty', 'final_price')
    list_filter = ('customer', 'product')
    search_fields = ('customer', 'product')
    form = CountProductValidation


class CartProductInline(CartProductFilterFKPAdmin, admin.TabularInline):
    model = models.CartProduct
    readonly_fields = ('final_price',)
    extra = 1
    form = CountProductValidation


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_product', 'final_price', 'in_order')
    inlines = [CartProductInline, ]
    list_filter = ('customer', 'in_order')
    search_fields = ('customer', 'in_order')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone', 'cart', 'status')
    list_editable = ('status',)
    list_filter = ('first_name', 'last_name', 'status')
    search_fields = ('first_name', 'last_name', 'status')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'qty', 'category', 'price')
    search_fields = ('name', 'category')


admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.CartProduct, CartProductAdmin)
admin.site.register(models.Cart, CartAdmin)
admin.site.register(models.Order, OrderAdmin)
