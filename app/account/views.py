from django.shortcuts import render, redirect
from django.views import View
from shop.utils import CartMixin, CategoryMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .services import *


@method_decorator(login_required, name='dispatch')
class ProfileView(CartMixin, View):
    template_name = 'account/profile.html'

    def get(self, request):
        categories = get_category()
        context = {
            'cart': self.cart_view,
            'categories': categories,
        }
        return render(request, self.template_name, context)


class LoginView(LoginView):
    template_name = 'account/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        return context


class RegistrationView(View):
    template_name = 'account/registration.html'

    def get(self, request):
        form = UserCreationForm()
        categories = get_category()
        context = {
            'categories': categories,
            'form': form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserCreationForm(request.POST)
        categories = get_category()
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
class DeleteOrderView(View):
    def get(self, request, id):
        delete_order(request, id)
        messages.success(request, "Заказ успешно отменен")
        return redirect('profile')
