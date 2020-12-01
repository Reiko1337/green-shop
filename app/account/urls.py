from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.ProfileView.as_view(), name='profile'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('reg/', views.RegistrationView.as_view(), name='reg'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('delete-order/<int:id>/', views.DeleteOrderView.as_view(), name='delete_order')

]
