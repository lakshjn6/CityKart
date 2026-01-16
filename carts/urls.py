from django.urls import path
from .views import carts
from .views import remove_cart
from .views import remove_cart_item
from .views import add_cart

urlpatterns = [
    path('', carts, name='carts'),
    path('add_cart/<int:product_id>/', add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/', remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/', remove_cart_item, name='remove_cart_item'),
    ]