from .models import Category, Cart, CartProduct, Order, Size
from django.views.generic.detail import SingleObjectMixin
from django.db import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .cart import CartSession, CartUserView


class CategoryMixin(SingleObjectMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class CartMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = get_object_or_404(User, username=request.user.username)
            cart = Cart.objects.filter(customer=user, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(customer=user)
            self.cart = cart
            self.cart_view = CartUserView(cart)
        else:
            self.cart = CartSession(request)
            self.cart_view = CartSession(request)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart_view
        return context


@receiver(post_delete, sender=CartProduct)
@receiver(post_save, sender=CartProduct)
def recalc_cart(sender, instance, **kwargs):
    cart = instance.cart
    cart_data = cart.cartproduct_set.all().aggregate(models.Sum('final_price'), models.Sum('qty'))
    if cart_data.get('final_price__sum') and cart_data.get('qty__sum'):
        cart.final_price = cart_data['final_price__sum']
        cart.total_product = cart_data['qty__sum']
    else:
        cart.final_price = 0
        cart.total_product = 0
    cart.save()


@receiver(post_delete, sender=Order)
def delete_order(sender, instance, **kwargs):
    cart = instance.cart
    for item in cart.cartproduct_set.all():
        product = item.product
        product.qty += item.qty
        product.save()
    cart.delete()


@receiver(post_delete, sender=Size)
@receiver(post_save, sender=Size)
def recalc_qty_product(instance, **kwargs):
    product = instance.product
    product_qty = product.size_set.all().aggregate(models.Sum('qty'))
    if product_qty.get('qty__sum'):
        product.qty = product_qty['qty__sum']
    else:
        product.qty = 0
    product.save()