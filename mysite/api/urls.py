
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

app_name = 'api'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'accounts', views.UserViewSet, basename='account') # Renamed from 'users' to match spec
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'stats', views.StatsViewSet, basename='stats')
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'contact', views.ContactViewSet, basename='contact')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    # JWT Token Endpoints for authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Cart endpoint (not a standard ViewSet)
    path('cart/', views.CartView.as_view(), name='cart'),
    
    # Include the viewset routes
    path('', include(router.urls)),
]
