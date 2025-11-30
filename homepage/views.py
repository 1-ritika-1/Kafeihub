from django.shortcuts import render 
from menu.models import MenuItem   
from reviews.models import Review 
from deals.models import Deal

def homepage_view(request):
    
    #Homepage view displaying featured menu items, deals, and reviews.
    # Fetches first 3 active items from each category for display. 
    # Also where model importing happens
    
    try:  # Get first 3 active items from each section
        menu_items = MenuItem.objects.filter(is_active=True)[:3]  # Get data from menu app
        deals = Deal.objects.filter(is_active=True)[:3]     # Get data from Deals app
        reviews = Review.objects.all().order_by('-date')[:3]   # Get data from Reviews app
    except Exception as e:
        # Log error and provide fallback...If database error, show empty sections
        menu_items = []
        deals = []
        reviews = []
    # Pass data to template
    context = {
        'menu_items': menu_items,
        'deals': deals,
        'reviews': reviews,
    }
    return render(request, 'homepage/home.html', context)