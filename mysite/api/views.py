
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count
from django_filters.rest_framework import DjangoFilterBackend
from catalog.models import Product, Category
from accounts.models import User
from orders.models import Order
from reviews.models import Review
from pages.models import Contact
from .serializers import (
    ProductSerializer, 
    CategorySerializer, 
    UserSerializer, 
    OrderSerializer,
    OrderCreateSerializer,
    ReviewSerializer,
    ContactSerializer
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

class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for product reviews.
    - `GET /api/v1/reviews/`: List all reviews.
    - `GET /api/v1/reviews/{id}/`: Retrieve a specific review.
    - `POST /api/v1/reviews/`: Create a new review.
    - `PATCH /api/v1/reviews/{id}/`: Update a review.
    - `DELETE /api/v1/reviews/{id}/`: Delete a review.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['product', 'rating']
    search_fields = ['comment']
    ordering_fields = ['created_at', 'rating']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ContactViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    API endpoint for contact form submissions.
    - `POST /api/v1/contact/`: Create a new contact message.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]

class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        return Response(cart, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        variant_id = request.data.get('variant_id')
        quantity = request.data.get('quantity', 1)

        if variant_id in cart:
            cart[variant_id]['quantity'] += quantity
        else:
            cart[variant_id] = {'quantity': quantity}
        
        request.session['cart'] = cart
        return Response(cart, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        variant_id = request.data.get('variant_id')
        quantity = request.data.get('quantity')

        if variant_id in cart:
            if quantity <= 0:
                del cart[variant_id]
            else:
                cart[variant_id]['quantity'] = quantity

        request.session['cart'] = cart
        return Response(cart, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        request.session['cart'] = {}
        return Response(status=status.HTTP_204_NO_CONTENT)

class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_checkout_session(self, request):
        # In a real application, you would integrate with a payment gateway like Stripe
        # and create a payment session here.
        return Response({'message': 'Payment session created successfully'}, status=status.HTTP_200_OK)

class StatsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request):
        total_sales = Order.objects.aggregate(total_sales=Sum('total'))['total_sales']
        total_orders = Order.objects.count()
        total_users = User.objects.count()

        return Response({
            'total_sales': total_sales,
            'total_orders': total_orders,
            'total_users': total_users
        }, status=status.HTTP_200_OK)
