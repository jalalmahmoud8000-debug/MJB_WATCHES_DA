
from django.db import models
from django.db.models import JSONField
import uuid
import os
from mptt.models import MPTTModel, TreeForeignKey
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

def product_image_path(instance, filename):
    """
    Generate file path for new product images.
    e.g., products/123/abc-123-def-456.jpg
    """
    ext = os.path.splitext(filename)[1]
    # get filename
    if instance.product.pk:
        filename = f'{uuid.uuid4()}{ext}'
        return os.path.join('products', str(instance.product.pk), filename)
    # else, this is a new product, so use a temporary path
    # we'll rename it later in a signal
    return os.path.join('products', 'temp', f'{uuid.uuid4()}{ext}')

def brand_logo_path(instance, filename):
    """
    Generate file path for new brand logos.
    e.g., brands/bikers/abc-123.png
    """
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('brands', instance.slug, filename)


class Category(MPTTModel):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    logo = models.ImageField(upload_to=brand_logo_path, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.CASCADE, null=True, blank=True)
    category = models.ManyToManyField(Category, related_name='products')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255, help_text="e.g., Red, Large")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    dimensions = JSONField(blank=True, null=True)
    attributes = JSONField(blank=True, null=True, help_text="e.g., {'color': 'Red', 'size': 'L'}")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('sku',)

    def __str__(self):
        return f'{self.product.name} - {self.name}'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=product_image_path)
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    # ImageKit fields
    thumbnail = ImageSpecField(source='image',
                                processors=[ResizeToFill(150, 150)],
                                format='WEBP',
                                options={'quality': 75})
    
    medium = ImageSpecField(source='image',
                            processors=[ResizeToFill(300, 300)],
                            format='WEBP',
                            options={'quality': 80})

    large = ImageSpecField(source='image',
                            processors=[ResizeToFill(800, 800)],
                            format='WEBP',
                            options={'quality': 85})


    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Ensure only one primary image per product
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super(ProductImage, self).save(*args, **kwargs)

    def __str__(self):
        return self.alt_text or f"Image for {self.product.name}"
