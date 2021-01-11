from .models import CartProduct, Cart, Category, Product
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def search_product(products, request):
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)
    else:
        products = products.all()
    return products


def make_order_user(request, order, cart):
    order.customer = request.user
    cart.in_order = True
    cart.save()
    for item in cart.cartproduct_set.all():
        product = item.product
        product.qty -= item.qty
        product.save()
    order.cart = cart
    order.save()


def make_order_anonymous_user(cart, order):
    cart_db = Cart.objects.create(total_product=cart.get_total_items(),
                                  final_price=cart.get_total_price(), in_order=True)
    for item in cart:
        CartProduct.objects.create(product=item['product'], cart=cart_db, qty=item['qty'],
                                   final_price=item['final_price'])
        product = item['product']
        product.qty -= item['qty']
        product.save()
    order.cart = cart_db
    order.save()
    cart.clear()


def get_products(request):
    products = Product.objects.all()
    return search_product(products, request)


def get_category():
    return Category.objects.all()


def get_category_name(slug):
    return get_object_or_404(Category, slug=slug)


def get_category_products(slug, request):
    category = get_category_name(slug)
    products = category.product_set.all()
    return search_product(products, request)


def delete_from_cart_product_id(id):
    cart_product = get_object_or_404(CartProduct, id=id)
    cart_product.delete()


def validation_checkout_user(request, cart):
    if request.user.is_authenticated:
        for item in cart.cartproduct_set.all():
            if item.product.qty < item.qty and item.product.qty != 0:
                cart_product = item
                cart_product.qty = item.product.qty
                cart_product.save()
                messages.error(request, 'Осталось только {0} товара {1}'.format(item.product.qty, item.product))
                return True
            if item.product.qty <= 0:
                messages.error(request, 'Товара нет в наличии {0}'.format(item.product.name))
                item.delete()
                return True


def validation_checkout_anonymous_user(request, cart_data):
    for item in cart_data.cart.values():
        product = get_object_or_404(Product, id=item['id'])
        if product.qty < item['qty'] and product.qty != 0:
            cart_data.change_qty(item['id'], product.qty)
            messages.error(request,
                           'Осталось только {0} товара {1}'.format(product.qty, product.name))
            return True
        if product.qty <= 0:
            messages.error(request, 'Товара нет в наличии {0}'.format(product.name))
            cart_data.remove(item['id'])
            return True


def change_qty(request, id, qty):
    cart_product = get_object_or_404(CartProduct, id=id)
    if cart_product.product.qty < qty:
        messages.error(request, 'Нет больше в наличии')
        return True
    cart_product.qty = qty
    cart_product.save()


def get_product_slug(slug):
    return get_object_or_404(Product, slug=slug)


def get_product_filter_slug(slug):
    return Product.objects.filter(slug=slug)


def add_to_cart_user(request, customer, cart, product):
    cart_product, created = CartProduct.objects.get_or_create(customer=customer, cart=cart,
                                                              product=product)
    if not created:
        if cart_product.qty < product.qty:
            cart_product.qty += 1
            cart_product.save()
        else:
            messages.error(request, 'Нет больше в наличии')
            return True


def email_message(order):
    subject = f'Заказ #{order.pk}'
    context = {'order_id': order.pk,
               'last_name': order.last_name,
               'first_name': order.first_name,
               'phone': order.phone,
               'address': order.address,
               'order_date': order.created_at,
               'items': order.cart.cartproduct_set.all()
               }
    message = render_to_string('shop/message_email.html', context)
    em = EmailMessage(subject=subject, body=message, to=[settings.EMAIL_MESSAGE_TO])
    em.send()
