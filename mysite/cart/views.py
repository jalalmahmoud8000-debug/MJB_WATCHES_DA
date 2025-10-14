
from django.shortcuts import render, get_object_or_404
from .models import Cart

def cart_detail(request):
    """ Display the user's current shopping cart. """
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart = get_object_or_404(Cart, id=cart_id)
    else:
        cart = None
    
    context = {
        'cart': cart
    }
    return render(request, 'cart/detail.html', context)
