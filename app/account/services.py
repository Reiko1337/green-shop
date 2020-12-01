from shop.models import Category, Order
from django.shortcuts import get_object_or_404


def get_category():
    return Category.objects.all()


def delete_order(request, id):
    order = get_object_or_404(Order, id=id, customer=request.user, status='new')
    for item in order.cart.cartproduct_set.all():
        product = item.product
        product.qty += item.qty
        product.save()
    order.cart.delete()
