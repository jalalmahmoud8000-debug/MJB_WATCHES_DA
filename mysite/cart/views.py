
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib import messages
from .models import Cart, CartItem
from catalog.models import ProductVariant

def create_cart(user):
    """Create a new cart, associated with a user if authenticated."""
    if user.is_authenticated:
        return Cart.objects.create(user=user)
    return Cart.objects.create()

class CartDetailView(TemplateView):
    template_name = 'cart/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.prefetch_related('items__variant__product__images').get(id=cart_id)
            except Cart.DoesNotExist:
                cart = None
        else:
            cart = None
        
        context['cart'] = cart
        return context

def add_to_cart(request):
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if not variant_id:
            return JsonResponse({'status': 'error', 'message': 'Variant not specified.'})

        variant = get_object_or_404(ProductVariant, id=variant_id)
        
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart = create_cart(request.user)
                request.session['cart_id'] = str(cart.id)
        else:
            cart = create_cart(request.user)
            request.session['cart_id'] = str(cart.id)
            
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            variant=variant,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            
        return JsonResponse({
            'status': 'success', 
            'message': 'Product added to cart.',
            'total': cart.get_total_price()
        })
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

def update_cart_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if not item_id or quantity < 1:
            return JsonResponse({'status': 'error', 'message': 'Invalid data.'})

        cart_item = get_object_or_404(CartItem, id=item_id)
        
        cart_id = request.session.get('cart_id')
        if not cart_id or str(cart_item.cart.id) != cart_id:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized.'})
            
        cart_item.quantity = quantity
        cart_item.save()
        
        cart = cart_item.cart
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Cart updated.',
            'total': cart.get_total_price(),
            'item_total': cart_item.get_total_price()
        })
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

def remove_from_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        
        if not item_id:
            return JsonResponse({'status': 'error', 'message': 'Invalid data.'})

        cart_item = get_object_or_404(CartItem, id=item_id)
        
        cart_id = request.session.get('cart_id')
        if not cart_id or str(cart_item.cart.id) != cart_id:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized.'})
            
        cart = cart_item.cart
        cart_item.delete()
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Item removed from cart.',
            'total': cart.get_total_price()
        })
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

def clear_cart(request):
    cart_id = request.session.get('cart_id')
    if cart_id:
        try:
            cart = Cart.objects.get(id=cart_id)
            cart.items.all().delete()
            messages.success(request, 'Your cart has been cleared.')
        except Cart.DoesNotExist:
            pass

    return redirect('cart:cart_detail')
