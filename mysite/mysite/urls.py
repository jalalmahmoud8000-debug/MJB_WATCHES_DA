
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pages.views import IndexView # Import the IndexView directly

urlpatterns = [
    # Homepage
    path('', IndexView.as_view(), name='index'), # Map the root URL to IndexView

    # Django Admin
    path('admin/', admin.site.urls),

    # API Versioning
    path('api/v1/', include('api.urls', namespace='v1')),
    
    # Other app URLs
    path('', include('pages.urls')),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('reviews/', include('reviews.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
