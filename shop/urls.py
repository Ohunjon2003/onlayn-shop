from django.urls import path
from .views import (rate, user_login, user_logout, user_register, cart, to_cart, product_list, all_products_list,
                    sorting_products_list, sorting_subcategory_list_view, product_detail_view, clear_cart,
                    create_checkout_sessions, success_payment)

urlpatterns = [
    path('', product_list, name='index'),
    path('products/', all_products_list, name='all_products'),
    path('sorting/<slug:key_name>/', sorting_products_list, name='sorting'),
    path('subcategory/<int:id>/', sorting_subcategory_list_view, name='sort_subcategory'),
    path('product/<slug:slug>/', product_detail_view, name='product_detail'),
    path('rate/<int:product_id>/<int:rating>/', rate),
    path('user-login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', user_register, name='user_register'),
    path('cart/', cart, name='cart'),
    path('to-cart/<int:product_id>/<str:action>/', to_cart, name='to_cart'),
    path('clear-cart/<int:product_id>', clear_cart, name='clear_cart'),
    path('payment/', create_checkout_sessions, name='payment'),
    path('success/', success_payment, name='success'),
]
