from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'category', 'image')
    list_filter = ('category',)
    search_fields = ('title', 'description')
    ordering = ('id',)