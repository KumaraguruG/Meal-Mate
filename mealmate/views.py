from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Customer, Restaurant, MenuItem, Cart
from django.contrib import messages  # To display messages to the user

import razorpay
from django.conf import settings


def index(request):
    return render(request, 'mealmate/index.html')

def signin(request):
    return render(request, 'mealmate/signin.html')

def signup(request):
    return render(request, 'mealmate/signup.html')

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
    restaurants = Restaurant.objects.all()      

    context = {
        'username': username,
        'restaurants': restaurants
    }
    return render(request, 'mealmate/customer_home.html', context)


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

def customer_menu(request, restaurant_id, username):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu_items = restaurant.menu_items.all()
    return render(request, 'mealmate/customer_menu.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'username':username
    })

def add_to_cart(request, item_id, username):
    customer = get_object_or_404(Customer, username=username)
    item = get_object_or_404(MenuItem, id=item_id)
    cart, created = Cart.objects.get_or_create(customer=customer)
    cart.items.add(item)
    messages.success(request, f"{item.name} added to your cart!")
    return redirect('customer_menu', restaurant_id=item.restaurant.id, username=username)

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

def orders(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()
    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0
    if cart:
        cart.items.clear()

    return render(request, 'mealmate/orders.html', {
        'username': username,
        'customer': customer,
        'cart_items': cart_items,
        'total_price': total_price,
    })