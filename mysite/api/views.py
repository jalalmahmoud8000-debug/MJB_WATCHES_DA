 
from rest_framework import viewsets, permissions, mixins
from django_filters.rest_framework import DjangoFilterBackend
from catalog.models import Product, Category
from accounts.models import User
from orders.models import Order
from .serializers import (
    ProductSerializer, 
    CategorySerializer, 
    UserSerializer, 
    OrderSerializer,
    OrderCreateSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows categories to be viewed.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny] # Allow public read-only access
    filterset_fields = ['name', 'parent__name'] 
    search_fields = ['name', 'description']
    ordering_fields = ['name']


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows products to be viewed.
    Supports filtering, searching, and ordering.
    """
    queryset = Product.objects.filter(is_active=True).prefetch_related('variants', 'images')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny] # Allow public read-only access
    filterset_fields = ['category__slug', 'brand', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'brand', 'created_at']
    ordering = ['-created_at']


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    RESTRICTED TO ADMINS.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser] # Only admins can view users
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['email', 'date_joined']


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
    API endpoint that allows users to create and view their orders.

    - `GET /api/v1/orders/`: List all of the user's orders.
    - `GET /api/v1/orders/{id}/`: Retrieve a specific order.
    - `POST /api/v1/orders/`: Create a new order.
    """
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'placed_at']
    ordering_fields = ['placed_at', 'total']
    ordering = ['-placed_at']

    def get_queryset(self):
        """
        This view returns a list of all the purchases for the
        currently authenticated user.
        Admins can see all orders.
        """
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().prefetch_related('items__variant__product')
        return Order.objects.filter(user=user).prefetch_related('items__variant__product')

    def get_serializer_class(self):
        """
        Use a different serializer for write operations.
        """
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

