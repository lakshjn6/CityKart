from carts.views import _cart_id
from carts.models import CartItem , Cart

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if cart.exists():
                cart_items = CartItem.objects.all().filter(cart__in=cart)
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0  
    return dict(cart_count=cart_count)
