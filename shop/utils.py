from .models import Product, OrderProduct, Customer, Order


class CartAuthenticatedUser:
    def __init__(self, request, product_id=None, action=None):
        self.request = request

        if product_id and action:
            self.add_or_delete(product_id, action)

    def get_cart_info(self):
        customer, created = Customer.objects.get_or_create(
            user=self.request.user
        )

        order, created = Order.objects.get_or_create(
            customer=customer
        )

        order_products = order.orderproduct_set.all()

        cart_total_price = order.get_cart_total_price
        cart_product_quantity = order.get_cart_quantity


        return {
            'order': order,
            'order_products': order_products,
            'cart_total_price': cart_total_price,
            'cart_product_quantity': cart_product_quantity
        }

    def add_or_delete(self, product_id, action):
        order = self.get_cart_info()['order']
        product = Product.objects.get(pk=product_id)
        order_product, created = OrderProduct.objects.get_or_create(
            order=order,
            product=product
        )
        if action == 'add'and product.quantity > 0:
            order_product.quantity += 1
            product.quantity -= 1
        elif action == 'delete':
            order_product.quantity -= 1
            product.quantity += 1
        order_product.save()
        product.save()

        if order_product.quantity <= 0:
            order_product.delete()




