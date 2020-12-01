from django.conf import settings
from .models import Product
from decimal import Decimal
from django.contrib import messages
from django.shortcuts import get_object_or_404


class CartSession(object):
    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        """
        Добавить продукт в корзину.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'id': product_id,
                'qty': 0,
                'price': str(product.price)
            }
        if self.cart[product_id]['qty'] < product.qty:
            self.cart[product_id]['qty'] += quantity
            self.save()
        else:
            messages.error(self.request, 'Нет больше в наличии')
            return True

    def change_qty(self, product, quantity):
        product_id = str(product)
        product = get_object_or_404(Product, id=product)
        if product.qty < quantity:
            messages.error(self.request, 'Нет больше в наличии')
            return True
        else:
            self.cart[product_id]['qty'] = quantity
            self.save()

    def save(self):
        # Обновление сессии cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отметить сеанс как "измененный", чтобы убедиться, что он сохранен
        self.session.modified = True

    def remove(self, id):
        product_id = str(id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных.
        """
        product_ids = self.cart.keys()
        # получение объектов product и добавление их в корзину
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product
        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['final_price'] = item['price'] * item['qty']
            yield item

    def get_total_items(self):
        """
        Подсчет всех товаров в корзине.
        """
        return sum(item['qty'] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        return sum(Decimal(item['price']) * item['qty'] for item in self.cart.values())

    def clear(self):
        # удаление корзины из сессии
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True


class CartUserView(object):
    def __init__(self, cart):
        self.final_price = cart.final_price
        self.cart_dict = {}
        for item in cart.cartproduct_set.all():
            self.cart_dict[str(item.id)] = {
                'id': str(item.id),
                'qty': item.qty,
                'final_price': item.final_price
            }
            self.cart_dict[str(item.id)]['product'] = item.product

    def __iter__(self):
        for item in self.cart_dict.values():
            yield item

    def get_total_items(self):
        return sum(item['qty'] for item in self.cart_dict.values())

    def get_total_price(self):
        return self.final_price

