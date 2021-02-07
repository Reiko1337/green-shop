from django.urls import path
from . import views

urlpatterns = [
    path('', views.MainPageView.as_view(), name='main_page'),
    path('product/<str:category>/<str:slug>/', views.DetailProductView.as_view(), name='product_detail'),
    path('product/<str:slug>', views.DetailCategoryView.as_view(), name='category_detail'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('add-to-cart/<str:slug>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/<str:id>/', views.DeleteFromCartView.as_view(), name='delete_from_cart'),
    path('change-qty/<str:id>/', views.ChangeQTYView.as_view(), name='change_qty'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('make-order/', views.MakeOrderView.as_view(), name='make_order'),
]
