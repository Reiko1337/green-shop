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
        if item.size is not None:
            size = item.size
            size.qty -= item.qty
            size.save()
        else:
            product = item.product
            product.qty -= item.qty
            product.save()
    order.cart = cart
    order.save()


def make_order_anonymous_user(cart, order):
    cart_db = Cart.objects.create(total_product=cart.get_total_items(),
                                  final_price=cart.get_total_price(), in_order=True)
    for item in cart:
        if item.get('size') is not None:
            CartProduct.objects.create(product=item['product'], cart=cart_db, size=item['size_obj'], qty=item['qty'],
                                       final_price=item['final_price'])
            size = item['size_obj']
            size.qty -= item['qty']
            size.save()
        else:
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
    for item in cart.cartproduct_set.all():
        if item.size:
            if item.size.qty < item.qty and item.size.qty != 0:
                cart_product = item
                cart_product.qty = item.size.qty
                cart_product.save()
                messages.error(request,
                               'Осталось только {0} товара {1} | Размер({2})'.format(item.size.qty, item.product,
                                                                                     item.size.size.normalize()))
                return True
            if item.size.qty <= 0:
                item.delete()
                messages.error(request,
                               'Товара нет в наличии {0} размера ({1})'.format(item.product.name, item.size.size))
                return True
        else:
            if item.product.qty < item.qty and item.product.qty != 0:
                cart_product = item
                cart_product.qty = item.product.qty
                cart_product.save()
                messages.error(request, 'Осталось только {0} товара {1}'.format(item.product.qty, item.product))
                return True
            if item.product.qty <= 0:
                item.delete()
                messages.error(request, 'Товара нет в наличии {0}'.format(item.product.name))
                return True


def validation_checkout_anonymous_user(request, cart_data, size_num=None):
    for item in cart_data.cart.values():
        if len(str(item['id']).split('-')) == 2:
            size_num = str(item['id']).split('-')[1]
        product_id = str(item['id']).split('-')[0]
        product_obj = get_object_or_404(Product, id=product_id)
        if size_num is not None:
            print(size_num)
            size = product_obj.size_set.filter(size=size_num).first()
            if size:
                if size.qty < item['qty'] and size.qty != 0:
                    cart_data.change_qty(item['id'], size.qty)
                    messages.error(request,
                                   'Осталось только {0} товара {1} | Размер({2})'.format(size.qty, product_obj.name,
                                                                                         size.size.normalize()))
                    return True
                if size.qty <= 0:
                    cart_data.remove(item['id'])
                    messages.error(request,
                                   'Товара нет в наличии {0} размера ({1})'.format(product_obj.name, size.size.normalize()))
                    return True
        else:
            if product_obj.qty < item['qty'] and product_obj.qty != 0:
                cart_data.change_qty(item['id'], product_obj.qty)
                messages.error(request,
                               'Осталось только {0} товара {1}'.format(product_obj.qty, product_obj.name))
                return True
            if product_obj.qty <= 0:
                messages.error(request, 'Товара нет в наличии {0}'.format(product_obj.name))
                cart_data.remove(item['id'])
                return True
        size_num = None

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
            return
    messages.success(request, "Товар успешно добавлен")


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


def get_size_sneaker(product: object) -> object:
    return product.size_set.order_by('size').all()


def add_to_cart(request, sizes_stock: list, product: object, cart: object):
    form_sizes = set(request.POST.values())
    size = set(map(lambda size: str(size.size.normalize()), sizes_stock))

    sizes = form_sizes & size
    if not sizes:
        return messages.info(request, f'Вы не выбрали размер Товара {product.name}')

    for size in sizes:
        size_num = sizes_stock.filter(size=size).first()
        if size_num:
            if request.user.is_authenticated:
                product_in_cart, create = CartProduct.objects.get_or_create(customer=cart.customer, cart=cart,
                                                                            product=product, size=size_num)
                if not create:
                    if product_in_cart.qty < size_num.qty:
                        product_in_cart.qty += 1
                        product_in_cart.save()
                    else:
                        messages.error(request,
                                       'Товар {0} | Размер ({1}) больше нет в наличии'.format(product.name, size))
                        continue
                messages.success(request, 'Товар {0} | Размер ({1}) добавлены в корзину'.format(product.name, size))
            else:
                cart.add_with_size(product, size_num)
