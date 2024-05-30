from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Category, Product, OrderProduct, ShippingAddress, Order, Customer


# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'discount', 'quantity', 'category', 'get_image')
    list_display_links = ('id', 'name')

    def get_image(self, product):
        if product.image:
            return mark_safe(f'<img src="{product.image.url}" width="75px;">')
        return '-'

    get_image.short_description = 'Rasmi'

    prepopulated_fields = {'slug': ('name',)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer']
    list_display_links = ['customer']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'firstname', 'lastname']
    list_display_links = ['user']


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'added']
    list_display_links = ['order']


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'address', 'city', 'district', 'mobile', 'zipcode']
    list_display_links = ['customer']