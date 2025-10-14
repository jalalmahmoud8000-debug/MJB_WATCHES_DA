
from django.db import transaction
from rest_framework import serializers
from catalog.models import Product, Category, ProductVariant, ProductImage
from accounts.models import User
from orders.models import Order, OrderItem


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text']


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'name', 'price', 'stock']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'brand', 'category', 'images', 'variants']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


# Optimized for displaying order details
class OrderItemSerializer(serializers.ModelSerializer):
    # Use a custom field to get the full product name
    product_name = serializers.CharField(source='variant.display_name', read_only=True)
    price = serializers.DecimalField(source='variant.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'price']

# Optimized for displaying orders
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'placed_at', 'items']

# --- Serializers for Writing Data ---

class CartItemSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ('items',)

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        # Start a database transaction
        with transaction.atomic():
            # Create the order instance
            order = Order.objects.create(user=user, status='pending')
            
            total_price = 0
            order_items = []

            for item_data in items_data:
                try:
                    variant = ProductVariant.objects.select_for_update().get(id=item_data['variant_id'])
                except ProductVariant.DoesNotExist:
                    raise serializers.ValidationError(f"Variant with id {item_data['variant_id']} not found.")

                # Check stock
                if variant.stock < item_data['quantity']:
                    raise serializers.ValidationError(f"Not enough stock for {variant.display_name}. Available: {variant.stock}")

                # Create OrderItem
                order_item = OrderItem(
                    order=order,
                    variant=variant,
                    quantity=item_data['quantity']
                )
                order_items.append(order_item)
                
                total_price += variant.price * item_data['quantity']
                
                # Decrease stock
                variant.stock -= item_data['quantity']

            # Bulk create the order items for efficiency
            OrderItem.objects.bulk_create(order_items)
            
            # Update variant stock in bulk
            ProductVariant.objects.bulk_update([item.variant for item in order_items], ['stock'])

            # Set the total price and save the order
            order.total = total_price
            order.save()

        return order
