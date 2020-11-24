from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from django.views.generic import DetailView
from .models import Product, Category, CartProduct
from .utils import CategoryMixin, CartMixin, recalc_cart
from django.shortcuts import get_object_or_404
from .forms import OrderForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
from django.contrib import messages


class MainPage(CartMixin, View):
    template_name = 'shop/main_page_shop.html'

    def get(self, request):
        products = Product.objects.all()
        search_query = request.GET.get('search', '')
        if search_query:
            products = products.filter(name__icontains=search_query)
        else:
            products = products.all()
        categories = Category.objects.all()
        context = {
            'products': products,
            'categories': categories,
            'cart': self.cart
        }
        return render(request, self.template_name, context)


class DetailProduct(CartMixin, CategoryMixin, DetailView):
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(slug=self.kwargs['slug'])


class DetailCategory(CartMixin, View):
    template_name = 'shop/category_detail.html'

    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        products = category.product_set.all()
        search_query = request.GET.get('search', '')
        if search_query:
            products = products.filter(name__icontains=search_query)
        else:
            products = products.all()
        categories = Category.objects.all()
        context = {
            'category_name':category,
            'products': products,
            'categories': categories,
            'cart': self.cart
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class Cart(CartMixin, View):
    template_name = 'shop/cart.html'

    def get(self, request):
        categories = Category.objects.all()
        context = {
            'categories': categories,
            'cart': self.cart
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class AddToCart(CartMixin, View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        product_qty = product.qty
        if not product_qty:
            messages.error(request, 'Товара нет в наличии')
            return redirect('main_page')
        cart_product, created = CartProduct.objects.get_or_create(customer=self.cart.customer, cart=self.cart,
                                                                  product=product)
        if not created:
            if cart_product.qty < product_qty:
                cart_product.qty += 1
                cart_product.save()
            else:
                messages.error(request, 'Нет больше в наличии')
                return redirect('cart')
        messages.success(request, "Товар успешно добавлен")
        return redirect('cart')


@method_decorator(login_required, name='dispatch')
class DeleteFromCart(CartMixin, View):
    def get(self, request, id):
        cart_product = get_object_or_404(CartProduct, id=id)
        cart_product.delete()
        messages.success(request, "Товар успешно удален")
        return redirect('cart')


@method_decorator(login_required, name='dispatch')
class ChangeQTYView(CartMixin, View):
    def post(self, request, id):
        qty = int(request.POST.get('qty'))
        cart_product = get_object_or_404(CartProduct, id=id)
        if cart_product.product.qty < qty:
            messages.error(request, 'Нет больше в наличии')
            return redirect('cart')
        cart_product.qty = qty
        cart_product.save()
        messages.success(request, "Кол-во успешно изменено")
        return redirect('cart')


@method_decorator(login_required, name='dispatch')
class Checkout(CartMixin, View):
    template_name = 'shop/checkout.html'

    def get(self, request):
        for item in self.cart.cartproduct_set.all():
            if item.product.qty < item.qty and item.product.qty != 0:
                cart_product = item
                cart_product.qty = item.product.qty
                cart_product.save()
                messages.error(request, 'Осталось только {0} товара {1}'.format(item.product.qty, item.product))
                return redirect('cart')
            if item.product.qty <= 0:
                messages.error(request, 'Товара нет в наличии {0}'.format(item.product.name))
                item.delete()
                return redirect('cart')
        categories = Category.objects.all()
        form = OrderForm(request.POST or None)
        if not self.cart.cartproduct_set.all().count():
            messages.error(request, "Ваша корзина покупок пуста")
            return redirect('main_page')
        context = {
            'cart': self.cart,
            'categories': categories,
            'form': form
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class MakeOrder(CartMixin, View):
    @transaction.atomic
    def post(self, request):
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user
            self.cart.in_order = True
            self.cart.save()
            for item in self.cart.cartproduct_set.all():
                product = item.product
                product.qty -= item.qty
                product.save()
            order.cart = self.cart
            order.save()
            messages.success(request, "Заказ оформлен")
            return redirect('main_page')
        return redirect('cart')
