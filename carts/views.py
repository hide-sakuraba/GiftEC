from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

@require_POST
def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, "商品をカートに追加しました。")
        else:
            messages.error(request, "在庫が不足しています。数量を増やすことはできません。")
    except CartItem.DoesNotExist:
        CartItem.objects.create(product=product, quantity=1, cart=cart)
        messages.success(request, "商品をカートに追加しました。")
    return redirect('carts:cart_detail')

@require_POST
def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        messages.success(request, "商品の数量を減らしました。")
    else:
        cart_item.delete()
        messages.success(request, "カートから商品を削除しました。")
    return redirect('carts:cart_detail')


@require_POST
def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    messages.success(request, "カートから商品を削除しました。")
    return redirect('carts:cart_detail')


def cart_detail(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    tax = int(total * 0.1)
    grand_total = total + tax

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'carts/cart.html', context)
