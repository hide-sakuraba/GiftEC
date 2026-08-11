import datetime
import uuid
import stripe
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from carts.models import Cart, CartItem
from carts.views import _cart_id
from .models import Order, OrderItem
from .forms import OrderForm
from products.models import Product


def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except Exception:
        return redirect('products:product_list')

    if not cart_items or cart_items.count() == 0:
        return redirect('products:product_list')

    tax = int(total * 0.1)
    grand_total = total + tax

    # Initialize Stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            if request.user.is_authenticated:
                data.user = request.user
            data.total_price = grand_total
            data.status = 'Pending'  # will be updated after payment
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            mt = int(datetime.date.today().strftime('%m'))
            dt = int(datetime.date.today().strftime('%d'))
            current_date = datetime.date(yr, mt, dt).strftime("%Y%m%d")
            order_number = f"{current_date}-{uuid.uuid4().hex[:8].upper()}"
            data.order_number = order_number
            data.save()

            for item in cart_items:
                OrderItem.objects.create(
                    order=data,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity,
                )

            # Create Stripe Checkout Session
            domain = request.build_absolute_uri('/')
            # 注意: success_url のパスは urls.py の order_complete パターンに合わせる
            success_url = domain + f"orders/order_complete/{order_number}/"
            cancel_url = domain + "cart/"
            line_items = []
            for item in cart_items:
                line_items.append({
                    'price_data': {
                        'currency': 'jpy',
                        'product_data': {'name': item.product.name},
                        # JPY は Stripe のゼロ小数点通貨のため * 100 は不要
                        'unit_amount': int(item.product.price),
                    },
                    'quantity': item.quantity,
                })
            if tax:
                line_items.append({
                    'price_data': {
                        'currency': 'jpy',
                        'product_data': {'name': '消費税'},
                        'unit_amount': tax,
                    },
                    'quantity': 1,
                })
            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    success_url=success_url,
                    cancel_url=cancel_url,
                    metadata={'order_number': order_number},
                )
            except stripe.error.StripeError as e:
                messages.error(request, f'決済の準備中にエラーが発生しました: {e.user_message}')
                data.delete()
                return redirect('orders:checkout')

            data.stripe_checkout_session_id = session.id
            data.save(update_fields=['stripe_checkout_session_id', 'updated_at'])
            request.session['order_access_numbers'] = list(
                set(request.session.get('order_access_numbers', []) + [order_number])
            )[-10:]

            return redirect(session.url, permanent=False)
        else:
            messages.error(request, '入力内容に不備があります。もう一度ご確認ください。')
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        form = OrderForm(initial=initial_data)

    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'orders/checkout.html', context)


def order_complete(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    is_owner = request.user.is_authenticated and order.user_id == request.user.id
    is_guest_order_in_session = order.user_id is None and order_number in request.session.get('order_access_numbers', [])
    if not (is_owner or is_guest_order_in_session):
        messages.error(request, 'この注文情報を表示する権限がありません。')
        return redirect('products:product_list')

    if order.status == 'Paid':
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            CartItem.objects.filter(cart=cart).delete()
        except Cart.DoesNotExist:
            pass
    order_items = OrderItem.objects.filter(order=order)
    subtotal = sum(item.sub_total() for item in order_items)

    context = {
        'order': order,
        'order_items': order_items,
        'subtotal': subtotal,
    }
    return render(request, 'orders/order_complete.html', context)


@csrf_exempt
def stripe_webhook(request):
    """
    Stripe Webhook エンドポイント。
    checkout.session.completed イベントを受信し、注文ステータスを Paid に更新する。
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    # 署名検証（改ざん防止）
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # ペイロードが不正
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # 署名が一致しない
        return HttpResponse(status=400)

    # checkout.session.completed イベントを処理
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_number = session.get('metadata', {}).get('order_number')
        if not order_number or session.get('payment_status') != 'paid':
            return HttpResponse(status=200)

        with transaction.atomic():
            try:
                order = Order.objects.select_for_update().get(
                    order_number=order_number,
                    stripe_checkout_session_id=session.get('id'),
                )
            except Order.DoesNotExist:
                return HttpResponse(status=200)

            if order.status != 'Pending':
                return HttpResponse(status=200)

            order_items = list(order.items.select_related('product').all())
            product_ids = [item.product_id for item in order_items]
            products = {
                product.id: product
                for product in Product.objects.select_for_update().filter(id__in=product_ids)
            }
            if any(products[item.product_id].stock < item.quantity for item in order_items):
                order.status = 'Cancelled'
                order.save(update_fields=['status', 'updated_at'])
                return HttpResponse(status=200)

            for item in order_items:
                product = products[item.product_id]
                product.stock -= item.quantity
                product.save(update_fields=['stock', 'updated_at'])

            order.status = 'Paid'
            order.stripe_payment_intent_id = session.get('payment_intent', '')
            order.save(update_fields=['status', 'stripe_payment_intent_id', 'updated_at'])

    return HttpResponse(status=200)
