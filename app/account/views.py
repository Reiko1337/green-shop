from django.shortcuts import render, redirect
from django.views import View
from shop.utils import CartMixin, CategoryMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from shop.models import Category, Order
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.contrib import messages


@method_decorator(login_required, name='dispatch')
class Profile(CartMixin, View):
    template_name = 'account/profile.html'

    def get(self, request):
        categories = Category.objects.all()
        context = {
            'cart': self.cart,
            'categories': categories,
        }
        return render(request, self.template_name, context)


class Login(LoginView):
    template_name = 'account/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class Registration(View):
    template_name = 'account/registration.html'

    def get(self, request):
        form = UserCreationForm()
        categories = Category.objects.all()
        context = {
            'categories': categories,
            'form': form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserCreationForm(request.POST)
        categories = Category.objects.all()
        context = {
            'categories': categories,
            'form': form
        }
        if form.is_valid():
            form.save()
            if request.user.is_authenticated:
                logout(request)
            return redirect('login')
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class DeleteOrder(View):
    def get(self, request, id):
        order = get_object_or_404(Order, id=id, customer=request.user, status='new')
        for item in order.cart.cartproduct_set.all():
            product = item.product
            product.qty += item.qty
            product.save()
        order.cart.delete()
        messages.success(request, "Заказ успешно отменен")
        return redirect('profile')
