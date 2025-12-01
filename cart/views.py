from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from menu.models import MenuItem
from deals.models import Deal
from .models import CartItem
from django.http import JsonResponse
import random

# -------------------------
# ADD MENU ITEM TO CART
# -------------------------

@login_required
def add_to_cart(request, product_id):
    print(f"Attempting to add product with ID: {product_id}")  # Debugging line
    
    product = get_object_or_404(MenuItem, id=product_id)
    
    print(f"Found product: {product.name}, {product.price}")  # Debugging line

    if request.method == "POST":
        try:
            # Get the quantity from the form, default to 1
            quantity = int(request.POST.get("quantity", 1))
            print(f"Quantity to add: {quantity}")  # Debugging line

            # Add or update cart item
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                item_type='MENU',
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            print(f"Item added/updated in cart: {cart_item.product.name} with quantity: {cart_item.quantity}")  # Debugging line

            # Return success response
            return JsonResponse({'success': True})

        except Exception as e:
            # If an error occurs, print it and return failure response
            print(f"Error adding item to cart: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# -------------------------
# ADD DEAL TO CART
# -------------------------
@login_required
def add_deal_to_cart(request, deal_id):
    deal = get_object_or_404(Deal, id=deal_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            deal=deal,
            item_type='DEAL',
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        # Redirect to cart after adding
        return redirect("cart:view_cart")

    # Redirect somewhere safe if GET request (user clicked URL directly)
    return redirect("deals:deals")

# -------------------------
# VIEW CART
# -------------------------
@login_required
def view_cart(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in items)

    # Get menu product suggestions
    cart_product_ids = items.values_list("product_id", flat=True)
    suggestions = list(MenuItem.objects.filter(is_active=True).exclude(id__in=cart_product_ids))
    random.shuffle(suggestions)
    suggestions = suggestions[:4]

    return render(request, "cart/cart.html", {
        "items": items,
        "total": total,
        "suggestions": suggestions
    })

# -------------------------
# UPDATE QUANTITY
# -------------------------
@login_required
def update_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    new_qty = int(request.POST.get("quantity"))

    if new_qty > 0:
        item.quantity = new_qty
        item.save()

    return redirect("cart:view_cart")

# -------------------------
# REMOVE ITEM
# -------------------------
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect("cart:view_cart")
