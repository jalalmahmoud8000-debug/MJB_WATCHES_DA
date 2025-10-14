
from .models import Cart

def cart(request):
    """
    A context processor to make the cart available on all pages.
    """
    cart_obj = None
    cart_id = request.session.get('cart_id')
    if cart_id:
        try:
            cart_obj = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            # If cart_id in session is invalid, remove it
            request.session.pop('cart_id', None)
            
    return {'cart': cart_obj}
