
import uuid
from django.db import models
from django.conf import settings
from catalog.models import ProductVariant


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Anonymous Cart - {self.session_key or self.id}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures a product variant can only appear once in a cart.
        # To change quantity, you update the existing record.
        unique_together = (('cart', 'variant'),)
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.quantity} x {self.variant.name} in cart {self.cart.id}'

    @property
    def subtotal(self):
        # Ensure variant has a price before calculating
        if self.variant and self.variant.price is not None:
            return self.variant.price * self.quantity
        return 0
