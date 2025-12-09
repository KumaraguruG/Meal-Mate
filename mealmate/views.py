from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Customer, Restaurant, MenuItem, Cart
from django.contrib import messages  # To display messages to the user

import razorpay
from django.conf import settings

# Home Page
def index(request):
    return render(request, 'mealmate/index.html')

# Sign In Page
def signin(request):
    return render(request, 'mealmate/signin.html')

# Sign Up Page
def signup(request):
    return render(request, 'mealmate/signup.html')

# Handle Login
def handle_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Check if the customer exists
            Customer.objects.get(username=username, password=password)
            
            if username == 'admin':
                return render(request, 'mealmate/admin_home.html')
            else:
                # Get first restaurant (or you can let user select later)
                restaurants = Restaurant.objects.all()

                return render(request, 'mealmate/customer_home.html', {
                    "restaurants": restaurants,
                    "username": username
                })
        except Customer.DoesNotExist:
            return render(request, 'mealmate/fail.html')
    return HttpResponse("Invalid request")

# Handle Sign Up
def handle_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        # Check for duplicate username
        if not Customer.objects.filter(username=username).exists():
            Customer.objects.create(
                username=username,
                password=password,
                email=email,
                mobile=mobile,
                address=address
            )
            return render(request, 'mealmate/signin.html')

    return HttpResponse("Invalid request")

def customer_home(request, username):
    restaurants = Restaurant.objects.all()      # fetch all restaurants

    context = {
        'username': username,
        'restaurants': restaurants
    }
    return render(request, 'mealmate/customer_home.html', context)


# Add Restaurant Page
def add_restaurant_page(request):
    return render(request, 'mealmate/add_restaurant.html')

# Add Restaurant
def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.FILES.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        Restaurant.objects.create(name = name, picture = picture, cuisine = cuisine, rating = rating)

        return redirect('show_restaurant_page')

# Show Restaurants
def show_restaurant_page(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'mealmate/show_restaurants.html', {"restaurants": restaurants})

# Restaurant Menu
def restaurant_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        is_veg = request.POST.get('is_veg') == 'on'
        picture = request.FILES.get('picture')

        MenuItem.objects.create(
            restaurant=restaurant,
            name=name,
            description=description,
            price=price,
            is_veg=is_veg,
            picture=picture
        )
        return redirect('restaurant_menu', restaurant_id=restaurant.id)

    menu_items = restaurant.menu_items.all()
    return render(request, 'mealmate/menu.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
    })

# Update Restaurant Page
def update_restaurant_page(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    return render(request, 'mealmate/update_restaurant_page.html', {"restaurant": restaurant})

# Update Restaurant
def update_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == 'POST':
        restaurant.name = request.POST.get('name')
        restaurant.picture = request.POST.get('picture')
        restaurant.cuisine = request.POST.get('cuisine')
        restaurant.rating = request.POST.get('rating')
        restaurant.save()

        restaurants = Restaurant.objects.all()
        return render(request, 'mealmate/show_restaurants.html', {"restaurants": restaurants})

# Delete Restaurant
def delete_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    restaurant.delete()

    restaurants = Restaurant.objects.all()
    return render(request, 'mealmate/show_restaurants.html', {"restaurants": restaurants})


# Update Menu item Page
def update_menuItem_page(request, menuItem_id):
    menuItem = get_object_or_404(MenuItem, id=menuItem_id)
    return render(request, 'mealmate/update_menuItem_page.html', {"item": menuItem})

# Update MenuItem
def update_menuItem(request, menuItem_id):
    menuItem = get_object_or_404(MenuItem, id=menuItem_id)

    if request.method == 'POST':
        menuItem.name = request.POST.get('name')
        menuItem.description = request.POST.get('description')
        menuItem.price = request.POST.get('price')
        menuItem.is_veg = request.POST.get('is_veg') == 'on'
        new_picture = request.FILES.get('picture')
        if new_picture:
            menuItem.picture = new_picture

        menuItem.save()

        restaurants = Restaurant.objects.all()
        return render(request, 'mealmate/show_restaurants.html', {"restaurants": restaurants})

# Delete menuItem
def delete_menuItem(request, menuItem_id):
    menuItem = get_object_or_404(MenuItem, id=menuItem_id)
    menuItem.delete()

    restaurants = Restaurant.objects.all()
    return render(request, 'mealmate/show_restaurants.html', {"restaurants": restaurants})


# Customer Menu
def customer_menu(request, restaurant_id, username):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = restaurant.menu_items.all()
    return render(request, 'mealmate/customer_menu.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'username':username
    })

# Add items to cart
def add_to_cart(request, item_id, username):
    # Check user and item
    customer = get_object_or_404(Customer, username=username)
    item = get_object_or_404(MenuItem, id=item_id)

    # Get or create a cart for the customer
    cart, created = Cart.objects.get_or_create(customer=customer)

    # Add the item to the cart
    cart.items.add(item)

    # Add a success message
    messages.success(request, f"{item.name} added to your cart!")

    # Stay on the same menu page
    return redirect('customer_menu', restaurant_id=item.restaurant.id, username=username)


# Show Cart
def show_cart_page(request, username):
    # Fetch the customer's cart
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    # Fetch cart items and total price
    items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    return render(request, 'mealmate/cart.html', {
        'items': items,
        'total_price': total_price,
        'username': username,
    })



# Checkout View
def checkout(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    if cart:
        cart_items = cart.items.all()
        total_price = sum(item.price for item in cart_items)
    else:
        cart_items = []
        total_price = 0

    amount = int(total_price * 100)
    # Razorpay should NOT stop page loading
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        order_id = order["id"]

    except Exception as e:
        return HttpResponse(f"Razorpay Error: {e}")

    return render(request, "mealmate/checkout.html", {
        "username": username,
        "cart_items": cart_items,
        "total_price": total_price,
        "amount": amount,
        "order_id": order_id,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
    })


# Orders Page
def orders(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    # Fetch cart items and total price before clearing the cart
    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    # Clear the cart after fetching its details
    if cart:
        cart.items.clear()

    return render(request, 'mealmate/orders.html', {
        'username': username,
        'customer': customer,
        'cart_items': cart_items,
        'total_price': total_price,
    })