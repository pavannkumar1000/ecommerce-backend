from django.urls import path
from .views import product_list, refresh_products

urlpatterns = [
    path('', product_list, name='product-list'),
    path('refresh/', refresh_products, name='refresh-products'),  # For admin
]