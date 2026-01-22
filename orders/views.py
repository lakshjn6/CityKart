from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import product as Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from django.views.decorators.csrf import csrf_exempt


import razorpay
from django.conf import settings


from django.http import HttpResponse



def payments(request):
    return render(request, 'orders/payments.html')

def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)

    if not cart_items.exists():
        return redirect('store')

    tax = 0
    for item in cart_items:
        total += item.prod.price * item.quantity
        quantity += item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.user = current_user
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address_line_1 = form.cleaned_data['address_line_1']
            order.address_line_2 = form.cleaned_data['address_line_2']
            order.city = form.cleaned_data['city']
            order.state = form.cleaned_data['state']
            order.country = form.cleaned_data['country']
            order.order_note = form.cleaned_data['order_note']
            order.order_total = grand_total
            order.tax = tax
            order.ip = request.META.get('REMOTE_ADDR')
            order.save()

            # Order Number
            order.order_number = f"{datetime.date.today().strftime('%Y%m%d')}{order.id}"
            order.save()

            # Razorpay Order
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )

            razorpay_order = client.order.create({
                'amount': int(grand_total * 100),  # paise
                'currency': 'INR',
                'payment_capture': 1
            })

            context = {
                'order': order,
                'cart_items': cart_items,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'amnt': int(grand_total),
                'amount': int(grand_total * 100),
            }

            return render(request, 'orders/payments.html', context)

    return redirect('checkout')


@csrf_exempt
def payment_success(request):
    body = json.loads(request.body)

    order_number = body.get('order_number')
    if not order_number:
        return JsonResponse({'error': 'order_number missing'}, status=400)

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=False)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    payment = Payment.objects.create(
        user=order.user,
        payment_id=body['razorpay_payment_id'],
        payment_method="Razorpay",
        amount_paid=order.order_total,
        status="Completed"
    )

    order.payment = payment
    order.is_ordered = True
    order.status = "Completed"
    order.save()

    cart_items = CartItem.objects.filter(user=order.user)

    for item in cart_items:
        OrderProduct.objects.create(
            order=order,
            payment=payment,
            user=order.user,
            product=item.prod,
            quantity=item.quantity,
            product_price=item.prod.price,
            ordered=True
        )

    cart_items.delete()

    return JsonResponse({'status': 'success'})


def order_success(request):
    order = Order.objects.filter(
        user=request.user,
        is_ordered=True
    ).order_by('-created_at').first()

    if not order:
        return redirect('store')

    return render(request, 'orders/order_success.html', {'order': order})
