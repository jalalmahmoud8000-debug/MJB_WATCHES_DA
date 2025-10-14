
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from catalog.models import Product


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    body = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        # A user can only write one review per product
        unique_together = (('product', 'user'),)

    def __str__(self):
        return f'Review for {self.product.name} by {self.user.email}'
