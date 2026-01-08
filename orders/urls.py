from django.urls import path
from .views import (
    get_cart, 
    add_to_cart, 
    remove_from_cart, 
    decrease_quantity, 
    checkout,
    order_history,
    order_detail,
    clear_cart
)

urlpatterns = [
    path('cart/', get_cart, name='get-cart'),
    path('cart/add/', add_to_cart, name='add-to-cart'),
    path('cart/remove/', remove_from_cart, name='remove-from-cart'),
    path('cart/decrease/', decrease_quantity, name='decrease-quantity'),
    path('cart/clear/', clear_cart, name='clear-cart'),
    path('cart/checkout/', checkout, name='checkout'),
    path('orders/', order_history, name='order-history'),
    path('orders/<int:order_id>/', order_detail, name='order-detail'),
]