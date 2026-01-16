from django.shortcuts import render, get_object_or_404
from .models import Cart, CartItem
from store.models import product
from django.shortcuts import redirect



# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    prod=product.objects.get(id=product_id)
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart=Cart.objects.create(
            cart_id=_cart_id(request)
        )
        cart.save() 
    try:
        cart_item=CartItem.objects.get(prod=prod,cart=cart)
        cart_item.quantity +=1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item=CartItem.objects.create(
            prod=prod,
            quantity=1,
            cart=cart
        )
        cart_item.save()    
    return redirect('carts')


def carts(request , total=0, quantity=0, cart_items=None):

    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.prod.price * cart_item.quantity)
            quantity += cart_item.quantity  
    except Cart.DoesNotExist:
        pass  # ignore
    tax= (2 * total)/100
    grand_total= total + tax
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/carts.html', context)

def remove_cart(request, product_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    prod=get_object_or_404(product, id=product_id)
    cart_item=CartItem.objects.get(prod=prod, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('carts')

def remove_cart_item(request, product_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    prod=get_object_or_404(product, id=product_id)
    cart_item=CartItem.objects.get(prod=prod, cart=cart)
    cart_item.delete()
    return redirect('carts')

