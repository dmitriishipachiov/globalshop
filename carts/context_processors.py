from .models import Cart

def cart_context(request):
    """
    Context processor to make cart information available globally in templates.

    Args:
        request (HttpRequest): The current request object.

    Returns:
        dict: A dictionary containing cart information including total quantity.
    """
    cart_data = {
        'total_quantity': 0,
    }

    try:
        # Get or create the cart for the current user/session
        cart = Cart.get_or_create_cart(request)

        # Calculate total quantity of items in cart
        if cart and cart.items.exists():
            cart_data['total_quantity'] = sum(item.quantity for item in cart.items.all())
    except Exception:
        # If there's any error, just return 0 quantity
        pass

    return cart_data