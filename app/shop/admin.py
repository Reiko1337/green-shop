from django.contrib import admin
from . import models
from django import forms
from django.utils.html import mark_safe
from django.template.loader import render_to_string

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


class CartProductAdmin(admin.ModelAdmin):
    readonly_fields = ('final_price', 'get_image_100')
    list_display = ('id', 'customer', 'product', 'get_image', 'cart', 'qty', 'final_price',)
    list_filter = ('customer', 'product')
    search_fields = ('customer', 'product')
    form = CountProductValidation

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.product.image.url} width="50">')

    def get_image_100(self, obj):
        return mark_safe(f'<img src={obj.product.image.url} width="200">')

    get_image_100.short_description = 'Изображение'
    get_image.short_description = 'Изображение'


class CartProductInline(admin.TabularInline):
    model = models.CartProduct
    readonly_fields = ('final_price', 'get_image_100')
    extra = 0
    form = CountProductValidation

    def get_image_100(self, obj):
        return mark_safe(f'<img src={obj.product.image.url} width="200">')

    get_image_100.short_description = 'Изображение'


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_product', 'final_price', 'in_order')
    inlines = [CartProductInline,]
    list_filter = ('customer', 'in_order')
    search_fields = ('customer', 'in_order')
    readonly_fields = ('final_price', 'total_product')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone', 'cart_product', 'final_price', 'status')
    list_editable = ('status',)
    list_filter = ('first_name', 'last_name', 'status')
    search_fields = ('first_name', 'last_name', 'status')
    readonly_fields = ('get_product_list',)

    def cart_product(self, obj):
        cart_products = obj.cart.cartproduct_set.all()
        return [f'{item.product.name}({item.qty})' for item in cart_products]

    cart_product.short_description = 'Товар'

    def final_price(self, obj):
        return obj.cart.final_price

    final_price.short_description = 'Цена'

    def get_product_list(self, obj):
        cart_products = obj.cart.cartproduct_set.all()
        return render_to_string('shop/order_admin.html', {
            'cart_products': cart_products,
            'total_product': obj.cart.total_product,
            'final_price': obj.cart.final_price
        })

    get_product_list.short_description = 'Список товаров'


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'qty', 'category', 'price', 'get_image')
    search_fields = ('name', 'category')
    readonly_fields = ('get_image_100',)

    def get_image_100(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="200">')

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="50">')

    get_image.short_description = 'Изображение'
    get_image_100.short_description = 'Изображение'


admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.CartProduct, CartProductAdmin)
admin.site.register(models.Cart, CartAdmin)
admin.site.register(models.Order, OrderAdmin)

admin.site.site_title = 'Ювелирный Магазин'
admin.site.site_header = 'Ювелирный Магазин'
