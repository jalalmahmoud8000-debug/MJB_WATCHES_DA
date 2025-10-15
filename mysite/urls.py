
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('orders/', include('orders.urls', namespace='orders')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('reviews/', include('product_reviews.urls', namespace='product_reviews')),
    path('', include('catalog.urls', namespace='catalog')),
]
