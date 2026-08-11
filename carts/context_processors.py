from .models import Cart, CartItem


def cart_processor(request):
    cart_count = 0
    try:
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.get(cart_id=session_key)
            cart_count = CartItem.objects.filter(cart=cart, is_active=True).count()
    except Cart.DoesNotExist:
        pass
    return {
        'cart_count': cart_count,
    }
