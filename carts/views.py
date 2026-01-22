from django.shortcuts import render, get_object_or_404
from .models import Cart, CartItem
from store.models import product
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import razorpay
from django.conf import settings

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    prod = get_object_or_404(product, id=product_id)

    if request.user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(prod=prod, user=request.user)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            CartItem.objects.create(
                prod=prod,
                quantity=1,
                user=request.user
            )
    else:
        cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))
        try:
            cart_item = CartItem.objects.get(prod=prod, cart=cart)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            CartItem.objects.create(
                prod=prod,
                quantity=1,
                cart=cart
            )

    return redirect('carts')



def carts(request , total=0, quantity=0, cart_items=None):

    try:
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user, is_active=True)
        else:
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

def remove_cart(request, product_id, cart_item_id):
    
    prod=get_object_or_404(product, id=product_id)
    if request.user.is_authenticated:
        cart_item=CartItem.objects.get(prod=prod, user=request.user ,id=cart_item_id)
    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_item=CartItem.objects.get(prod=prod, cart=cart , id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('carts')

def remove_cart_item(request, product_id , cart_item_id):
    
    prod=get_object_or_404(product, id=product_id)
    if request.user.is_authenticated:
        cart_item=CartItem.objects.get(prod=prod, user=request.user , id=cart_item_id)
    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_item=CartItem.objects.get(prod=prod, cart=cart , id=cart_item_id)   
    cart_item.delete()
    return redirect('carts')




@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):

    try:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)

        for cart_item in cart_items:
            total += cart_item.prod.price * cart_item.quantity
            quantity += cart_item.quantity

    except CartItem.DoesNotExist:
        pass

    tax = (2 * total) / 100
    grand_total = total + tax
    client = razorpay.Client(auth=(
    settings.RAZORPAY_KEY_ID,
    settings.RAZORPAY_KEY_SECRET,))

    razorpay_order = client.order.create({
    "amount": int(grand_total * 100),  # paise
    "currency": "INR",
    "payment_capture": "1"})

    
    context = {
    'total': total,
    'quantity': quantity,
    'cart_items': cart_items,
    'tax': tax,
    'grand_total': grand_total,
    'razorpay_key': settings.RAZORPAY_KEY_ID,
    'razorpay_order_id': razorpay_order['id'],
    'razorpay_amount': int(grand_total * 100),}

    return render(request, 'store/checkout.html', context)

