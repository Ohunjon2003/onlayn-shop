from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Kategoriya")
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                               null=True, blank=True,
                               related_name='subcategories')

    def __str__(self):
        return self.name


FILTER_CHOICES = {
    'po': 'Popularity',
    'org': 'Organic',
    'fan': 'Fantastic'
}


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategoriya")
    filter_choice = models.CharField(max_length=3, choices=FILTER_CHOICES, null=True)
    name = models.CharField(max_length=255, verbose_name="Nomi")
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    discount = models.FloatField(null=True, blank=True)
    quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', verbose_name="Rasmi")
    slug = models.SlugField(null=True, blank=True)

    def average_rating(self) -> float:
        return Rating.objects.filter(post=self).aggregate(Avg("rating"))["rating__avg"] or 0

    def __str__(self):
        return self.name


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name}: {self.rating}"


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Mijoz", null=True)
    firstname = models.CharField(max_length=100, verbose_name="Ismi")
    lastname = models.CharField(max_length=100, verbose_name="Familiyasi")

    def __str__(self):
        return f"{self.user}"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, verbose_name="Mijoz", null=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Xarid vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Xolat")

    def __str__(self):
        return f"{self.customer}"

    @property
    def get_cart_total_price(self):
        order_products = self.orderproduct_set.all()
        total_price = sum([product.get_cart_price for product in order_products])
        return total_price

    @property
    def get_cart_quantity(self):
        order_products = self.orderproduct_set.all()
        totat_quantity = [product.quantity for product in order_products]
        total_quantity_sum = sum(totat_quantity)
        return total_quantity_sum


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, verbose_name="Xarid", null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, verbose_name="Maxsulot", null=True)
    quantity = models.IntegerField(default=0, verbose_name="Soni")
    added = models.DateTimeField(auto_now_add=True, verbose_name="Xarid vaqti")

    def __str__(self):
        return f"{self.product}"

    @property
    def get_cart_price(self):
        total_price = self.quantity * self.product.price
        return total_price


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, verbose_name="Mijoz", null=True)
    address = models.CharField(max_length=255, verbose_name="Manzil")
    city = models.CharField(max_length=255, verbose_name="Shahar")
    district = models.CharField(max_length=50, verbose_name="Tuman")
    zipcode = models.CharField(max_length=100, verbose_name="Pochta kodi")
    mobile = models.CharField(max_length=100, verbose_name="Mobil raqami")
    email = models.EmailField(verbose_name="Email manzili", max_length=100)

    def __str__(self):
        return f"{self.customer}"
