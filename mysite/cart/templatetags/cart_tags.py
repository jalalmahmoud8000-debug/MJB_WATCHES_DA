
from django import template
from ..models import Cart

register = template.Library()

@register.simple_tag(takes_context=True)
def cart_item_count(context):
    request = context['request']
    cart_id = request.session.get('cart_id')
    if cart_id:
        try:
            cart = Cart.objects.get(id=cart_id)
            return cart.items.count()
        except Cart.DoesNotExist:
            return 0
    return 0
