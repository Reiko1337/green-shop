from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import DetailView
from .utils import CategoryMixin, CartMixin
from .forms import OrderForm
from django.db import transaction
from .services import *


class MainPageView(CartMixin, View):
    template_name = 'shop/main_page_shop.html'

    def get(self, request):
        products = get_products(request)
        categories = get_category()
        context = {
            'products': products,
            'categories': categories,
            'cart': self.cart_view,
        }
        return render(request, self.template_name, context)


class DetailProductView(CartMixin, CategoryMixin, DetailView):
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return get_product_filter_slug(self.kwargs['slug'])


class DetailCategoryView(CartMixin, View):
    template_name = 'shop/category_detail.html'

    def get(self, request, slug):
        products = get_category_products(slug, request)
        categories = get_category()
        context = {
            'category_name': get_category_name(slug),
            'products': products,
            'categories': categories,
            'cart': self.cart_view,
        }
        return render(request, self.template_name, context)


class CartView(CartMixin, View):
    template_name = 'shop/cart.html'

    def get(self, request):
        categories = get_category()
        context = {
            'categories': categories,
            'cart': self.cart_view
        }
        return render(request, self.template_name, context)


class AddToCartView(CartMixin, View):
    def get(self, request, slug):
        product = get_product_slug(slug)
        if not product.qty:
            messages.error(request, 'Товара нет в наличии')
            return redirect('main_page')
        if request.user.is_authenticated:
            if add_to_cart_user(request, self.cart.customer, self.cart, product):
                return redirect(request.META.get('HTTP_REFERER'))
        else:
            if self.cart.add(product):
                return redirect(request.META.get('HTTP_REFERER'))
        messages.success(request, "Товар успешно добавлен")
        return redirect(request.META.get('HTTP_REFERER'))


class DeleteFromCartView(CartMixin, View):
    def get(self, request, id):
        if request.user.is_authenticated:
            delete_from_cart_product_id(id)
        else:
            self.cart.remove(id)
        messages.success(request, "Товар успешно удален")
        return redirect('cart')


class ChangeQTYView(CartMixin, View):
    def post(self, request, id):
        qty = int(request.POST.get('qty'))
        if request.user.is_authenticated:
            if change_qty(request, id, qty):
                return redirect('cart')
        else:
            if self.cart.change_qty(id, quantity=qty):
                return redirect('cart')
        messages.success(request, "Кол-во успешно изменено")
        return redirect('cart')


class CheckoutView(CartMixin, View):
    template_name = 'shop/checkout.html'

    def get(self, request):
        if request.user.is_authenticated:
            if validation_checkout_user(request, self.cart):
                return redirect('cart')
        else:
            if validation_checkout_anonymous_user(request, self.cart):
                return redirect('cart')
        categories = get_category()
        if not self.cart_view.get_total_items():
            messages.error(request, "Ваша корзина покупок пуста")
            return redirect('main_page')
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart_view,
            'categories': categories,
            'form': form
        }
        return render(request, self.template_name, context)


class MakeOrderView(CartMixin, View):
    @transaction.atomic
    def post(self, request):
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                make_order_user(request, order, self.cart)
            else:
                make_order_anonymous_user(self.cart, order)
            email_message(order)
            messages.success(request, "Заказ оформлен")
            return redirect('main_page')
        return redirect('cart')

