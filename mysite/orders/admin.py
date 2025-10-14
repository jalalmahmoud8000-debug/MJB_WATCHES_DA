
from django.contrib import admin
from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('variant', 'quantity', 'price_at_purchase')
    extra = 0
    readonly_fields = ('price_at_purchase',)
    autocomplete_fields = ['variant']


class PaymentInline(admin.TabularInline):
    model = Payment
    fields = ('provider', 'status', 'amount', 'transaction_id')
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'placed_at')
    list_filter = ('status', 'placed_at')
    search_fields = ('id', 'user__email', 'tracking_number')
    readonly_fields = ('placed_at', 'total')
    autocomplete_fields = ['user', 'shipping_address', 'billing_address']
    inlines = [OrderItemInline, PaymentInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'variant', 'quantity', 'price_at_purchase')
    search_fields = ('order__id', 'variant__sku', 'variant__name')
    autocomplete_fields = ['order', 'variant']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'provider', 'status', 'amount', 'transaction_id')
    list_filter = ('status', 'provider')
    search_fields = ('order__id', 'transaction_id')
    autocomplete_fields = ['order']
