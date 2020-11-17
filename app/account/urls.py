from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.Profile.as_view(), name='profile'),
    path('login/', views.Login.as_view(), name='login'),
    path('reg/', views.Registration.as_view(), name='reg'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('delete-order/<int:id>/', views.DeleteOrder.as_view(), name='delete_order')

]
