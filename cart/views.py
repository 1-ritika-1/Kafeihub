from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from menu.models import MenuItem
from .models import CartItem
from django.http import JsonResponse


# ADD TO CART (AJAX ENABLED)
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(MenuItem, id=product_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )

        # If already exists, increase by chosen quantity
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        # If AJAX request -> return JSON instead of redirect
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True, "message": "Item added to cart!"})

        return redirect("cart:view_cart")

    return JsonResponse({"success": False}, status=400)



# VIEW CART
@login_required
def view_cart(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in items)

    return render(request, "cart/cart.html", {
        "items": items,
        "total": total
    })


# UPDATE QUANTITY
@login_required
def update_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    new_qty = int(request.POST.get("quantity"))

    if new_qty > 0:
        item.quantity = new_qty
        item.save()

    return redirect("cart:view_cart")


# REMOVE ITEM
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect("cart:view_cart")
