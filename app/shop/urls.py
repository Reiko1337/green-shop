from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.MainPage.as_view(), name='main_page'),
    path('product/<str:category>/<str:slug>/', views.DetailProduct.as_view(), name='product_detail'),
    path('product/<str:slug>', views.DetailCategory.as_view(), name='category_detail'),
    path('cart/', views.Cart.as_view(), name='cart'),
    path('add-to-cart/<str:slug>/', views.AddToCart.as_view(), name='add_to_cart'),
    path('remove-from-cart/<int:id>/', views.DeleteFromCart.as_view(), name='delete_from_cart'),
    path('change-qty/<int:id>/', views.ChangeQTYView.as_view(), name='change_qty'),
    path('checkout/', views.Checkout.as_view(), name='checkout'),
    path('make-order/', views.MakeOrder.as_view(), name='make_order')
]
