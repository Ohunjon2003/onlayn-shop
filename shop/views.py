
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from .models import Category, Product, Rating
from .forms import LoginForm, RegisterForm
from .utils import CartAuthenticatedUser
from django.http import HttpRequest

def product_list(request):
    products = Product.objects.all()
    cart_info = CartAuthenticatedUser(request)
    categories = Category.objects.filter(parent=None)
    title = "Fruitables online shop"
    context = {
        'products': products,
        'categories': categories,
        'title': title,
        'cart_product_quantity': cart_info.get_cart_info()['cart_product_quantity']
    }
    return render(request, 'shop/index.html', context)

def all_products_list(request):
    products = Product.objects.all()
    categories = Category.objects.filter(parent=None)
    cart_info = CartAuthenticatedUser(request)
    title = "Fruitables online shop"
    context = {
        'products': products,
        'categories': categories,
        'cart_product_quantity': cart_info.get_cart_info()['cart_product_quantity'],
        'title': title
    }
    return render(request, 'shop/all_products.html', context)

def sorting_products_list(request, key_name):
    products = Product.objects.filter(filter_choice=key_name)
    context = {
        'products': products
    }
    return render(request, 'shop/all_products.html', context)

def sorting_subcategory_list_view(request, id):
    products = Product.objects.filter(category_id=id)
    categories = Category.objects.filter(parent=None)
    context = {
        'products': products,
        'categories': categories
    }
    return render(request, 'shop/all_products.html', context)

def product_detail_view(request, slug):
    product = Product.objects.get(slug=slug)
    cart_info = CartAuthenticatedUser(request)
    categories = Category.objects.filter(parent=None)
    all_products = Product.objects.all()
    user_rating = 0
    if request.user.is_authenticated:
        rating = Rating.objects.filter(product=product, user=request.user).first()
        user_rating = rating.rating if rating else 0
    else:
        messages.error(request, 'Baholash uchun tizimga kiring!')
    context = {
        'product': product,
        'categories': categories,
        'cart_product_quantity': cart_info.get_cart_info()['cart_product_quantity'],
        'products': all_products,
        'title': 'Shop detail',
        'user_rating': user_rating
    }
    return render(request, 'shop/product_detail.html', context)

def rate(request: HttpRequest, product_id: int, rating: int) -> HttpResponse:
    product = Product.objects.get(pk=product_id)
    if request.user.is_authenticated:
        Rating.objects.filter(product=product, user=request.user).delete()
        product.rating_set.create(user=request.user, rating=rating)
    return redirect('product_detail', slug=product.slug)


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'{user.username}, siz saytga muvaffaqiyatli kirdingiz!')
            return redirect('index')
    else:
        form = LoginForm()
    return render(request, 'shop/user_login.html', {'form': form, 'title': 'Tizimga kirish'})


def user_logout(request):
    logout(request)
    return redirect('login')


def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        username = request.POST.get('username')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Bu username mavjud. Boshqa username tanlang.')
            return redirect('user_register')
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'{user.username}, siz saytga muvaffaqiyatli ro\'yxatdan o\'tdingiz!')
            return redirect('index')
    else:
        form = RegisterForm()

    context = {
        'form': form,
        'title': 'Ro\'yxatdan o\'tish'
    }
    return render(request, 'shop/user_register.html', context)


def cart(request):
    cart_info = CartAuthenticatedUser(request)
    context = {
        'order_products': cart_info.get_cart_info()['order_products'],
        'cart_total_price': cart_info.get_cart_info()['cart_total_price'],
        'cart_product_quantity': cart_info.get_cart_info()['cart_product_quantity'],
        'title': 'Savat'
    }
    return render(request, 'shop/cart.html', context)


def to_cart(request: HttpRequest, product_id, action):
    if request.user.is_authenticated:
        CartAuthenticatedUser(request, product_id, action)
        current_page = request.META.get('HTTP_REFERER', 'all_products')
        return redirect(current_page)
    return redirect('user_login')


def clear_cart(request, product_id):
    if request.user.is_authenticated:
        cart_info = CartAuthenticatedUser(request)
        order = cart_info.get_cart_info()['order']
        order_product = order.orderproduct_set.get(product_id=product_id)
        product = order_product.product
        product.quantity += order_product.quantity
        product.save()
        order_product.delete()
        return redirect('cart')
    else:
        return redirect('login')


def create_checkout_sessions(request, stripe=None):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    user_cart = CartAuthenticatedUser(request)
    cart_info = user_cart.get_cart_info()
    total_price = cart_info['cart_total_price']
    total_quantity = cart_info['cart_product_quantity']
    session = stripe.checkout.Session.create(
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Online Shop mahsulotlari'
                },
                'unit_amount': int(total_price * 100)
            },
            'quantity': total_quantity
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('success')),
        cancel_url=request.build_absolute_uri(reverse('success')),
    )
    return redirect(session.url, 303)


def success_payment(request):
    return render(request, 'shop/success.html')