
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Order
from catalog.models import ProductVariant

@staff_member_required
def dashboard(request):
    """
    A view for the admin dashboard to display key sales and inventory metrics.
    """
    today = timezone.now().date()
    
    # 1. Sales for today
    today_sales = Order.objects.filter(placed_at__date=today, status__in=['PROCESSING', 'SHIPPED', 'DELIVERED']).aggregate(total_sales=Sum('total'))['total_sales'] or 0
    
    # 2. Recent orders (last 5)
    recent_orders = Order.objects.order_by('-placed_at')[:5]
    
    # 3. Low stock items (stock < 10)
    low_stock_threshold = 10
    low_stock_items = ProductVariant.objects.filter(stock__lt=low_stock_threshold).order_by('stock')
    
    # 4. General statistics
    stats = {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='PENDING').count(),
        'total_sales': Order.objects.filter(status__in=['PROCESSING', 'SHIPPED', 'DELIVERED']).aggregate(total=Sum('total'))['total'] or 0,
    }

    context = {
        'today_sales': today_sales,
        'recent_orders': recent_orders,
        'low_stock_items': low_stock_items,
        'low_stock_threshold': low_stock_threshold,
        'stats': stats,
        # These are for the admin base template
        'title': 'Dashboard',
        'site_title': 'My Site Admin',
        'site_header': 'My Site Administration',
        'has_permission': True,
        'is_popup': False,
        'is_nav_sidebar_enabled': True,
    }
    
    return render(request, 'orders/dashboard.html', context)

@login_required
def order_list(request):
    """Display a list of orders for the current user."""
    orders = Order.objects.filter(user=request.user).order_by('-placed_at')
    context = {
        'orders': orders
    }
    return render(request, 'orders/order/list.html', context)

@login_required
def order_detail(request, order_id):
    """Display the details of a specific order."""
    order = get_object_or_404(Order, id=order_id, user=request.user) # Ensure order belongs to user
    context = {
        'order': order
    }
    return render(request, 'orders/order/detail.html', context)
