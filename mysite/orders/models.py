
import uuid
from django.db import models
from django.conf import settings
from catalog.models import ProductVariant
from accounts.models import Address


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_address = models.ForeignKey(
        Address, related_name='shipping_orders', on_delete=models.SET_NULL, null=True, blank=True
    )
    billing_address = models.ForeignKey(
        Address, related_name='billing_orders', on_delete=models.SET_NULL, null=True, blank=True
    )
    placed_at = models.DateTimeField(auto_now_add=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-placed_at']

    def __str__(self):
        return f"Order {self.id} by {self.user.email if self.user else 'Guest'}"

    def update_total(self):
        """Recalculates the order total based on its items."""
        self.total = sum(item.subtotal for item in self.items.all()) or 0
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, related_name='order_items', on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.variant.name if self.variant else 'Deleted Product'} for Order {self.order.id}"

    @property
    def subtotal(self):
        return self.price_at_purchase * self.quantity


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCEEDED = 'SUCCEEDED', 'Succeeded'
        FAILED = 'FAILED', 'Failed'

    order = models.ForeignKey(Order, related_name='payments', on_delete=models.CASCADE)
    provider = models.CharField(max_length=50) # e.g., 'Stripe', 'PayPal'
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, unique=True)
    metadata = models.JSONField(blank=True, null=True) # To store raw response from payment provider
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.status} for Order {self.order.id} via {self.provider}"
