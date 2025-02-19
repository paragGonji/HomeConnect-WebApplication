from decimal import Decimal
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
import razorpay

from delivery.models import DeliveryOrder
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required
from django.conf import settings  # For fetching delivery API URL
import requests 

from kitchen.models import KitchenDish  # Importing from kitchen app
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
# receipes page test
@login_required(login_url="/login/")
def receipes(request):
    queryset = KitchenDish.objects.filter(is_available=True)  # Only available dishes
    
    search_query = request.GET.get('search')
    if search_query:
        queryset = queryset.filter(dish_name__icontains=search_query)
    
    context = {'recipes': queryset}  # Pass the data to the template
    return render(request, 'receipes.html', context)

# login resturant
def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')


        if not User.objects.filter(username = username).exists():
            messages.error(request, "Invalid Username")
            return redirect('/login/')
        

        user = authenticate(username = username, password = password)

        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('/login/')
        else:
            login(request, user)
            return redirect('/homeconnect/')
    return render(request , 'login.html')

# logout
def logout_page(request):
    logout(request)
    return redirect('/login/')

# registration for login for food 
def register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the username already exists
        user = User.objects.filter(username=username)
        if user.exists():
            messages.error(request, "Username already taken !!")
            return redirect('/register/')

        # Create the user
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save()

        messages.info(request, "Account Created Successfully!")
        return redirect('/register/')
    return render(request, 'register.html')

def testsessions(request):
    if request.session.get('test', False):
        print(request.session["test"])
    #request.session.set_expiry(1)
    # if request.session['test']:
    #     print(request.session['test'])
    request.session['test'] = "testing"
    request.session['test2'] = "testing2"
    return render(request, "kitchen_register.html")

@login_required(login_url="/login/")
def homeconnect(request):

    return render(request , 'homeconnect.html')

@login_required(login_url="/login/")
def popular(request):
    queryset = KitchenDish.objects.filter(is_available=True)  # Fetch only available dishes

    search_query = request.GET.get('search')
    if search_query:
        queryset = queryset.filter(dish_name__icontains=search_query)  # Search filter

    context = {'recipes': queryset}  # Passing data to template
    return render(request, 'popular.html', context)

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: decimal_to_float(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(item) for item in obj]
    return obj

@login_required(login_url="/login/")
def add_to_cart(request):
    dish_id = request.POST.get('dish_id')
    quantity = int(request.POST.get('quantity', 1))  # Default quantity is 1
    
    if dish_id:
        # Get the selected dish object
        dish = KitchenDish.objects.get(id=dish_id)
        
        # Add the dish to the cart (stored in session)
        cart = request.session.get('cart', {})
        
        if dish_id in cart:
            cart[dish_id]['quantity'] += quantity
        else:
            cart[dish_id] = {
                'name': dish.dish_name, 
                'price': decimal_to_float(dish.dish_price),  # Convert price to float
                'quantity': quantity, 
                'image': dish.dish_image.url,
                'time': dish.preparation_time,  # Ensure 'time' key exists
                'loaction' : dish.kitchen.kitchen_address
            } 
        
        # Save cart back to the session
        request.session['cart'] = cart
        messages.success(request, f'{dish.dish_name} added to cart!')
    
    return redirect('receipes')

@login_required(login_url="/login/")
def cart(request):
    # Get the cart from session
    cart = request.session.get('cart', {})
    user_details = request.session.get('user_details', {'phone_number': '', 'uservege_address': ''})

    if not cart:
        messages.info(request, 'Your cart is empty.')

    # Initialize total price
    total_price = 0

    # Calculate total price and ensure all Decimal values are converted to float
    for item in cart.values():
        total_price += decimal_to_float(item['price']) * item['quantity']

    context = {
        'cart': cart,
        'total_price': total_price,
        'user_details': user_details,  # Pass user details to template
        'razorpay_key': settings.RAZORPAY_KEY_ID  # Pass Razorpay key to the template
    }
    return render(request, 'cart.html', context)

@login_required(login_url="/login/")
def save_user_details(request):
    if request.method == "POST":
        phone_number = request.POST.get('phone_number', '').strip()
        uservege_address = request.POST.get('uservege_address', '').strip()

        if phone_number and uservege_address:
            request.session['user_details'] = {
                'phone_number': phone_number,
                'uservege_address': uservege_address,
            }
            messages.success(request, "User details saved successfully!")

    return redirect('cart')  # Redirect back to cart

@login_required(login_url="/login/")
def update_quantity(request, item_id):
    if request.method == "POST":
        print(f"Update Quantity Request Received for item_id: {item_id}")  # Debugging
        new_quantity = int(request.POST.get('quantity', 1))
        print(f"New Quantity: {new_quantity}")  # Debugging
        cart = request.session.get('cart', {})
        if str(item_id) in cart:  # Ensure item_id is a string for dictionary lookup
            cart[str(item_id)]['quantity'] = new_quantity
            request.session['cart'] = cart
            messages.success(request, f'Quantity updated to {new_quantity}')
        else:
            messages.error(request, 'Item not found in cart.')
    return redirect('cart')

@login_required(login_url="/login/")
def delete_item(request, item_id):
    if request.method == "POST":
        print(f"Delete Item Request Received for item_id: {item_id}")  # Debugging
        cart = request.session.get('cart', {})
        if str(item_id) in cart:  # Ensure item_id is a string for dictionary lookup
            del cart[str(item_id)]
            request.session['cart'] = cart
            messages.success(request, 'Item removed from cart!')
        else:
            messages.error(request, 'Item not found in cart.')
    return redirect('cart')

@csrf_exempt
def receive_order(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            print("Received order data:", data)  # Debugging: Print the received data

            # Process the order data (save to database, etc.)
            # Example: Save the order to the database
            # DeliveryOrder.objects.create(user_id=data['user_id'], items=data['items'], total_price=data['total_price'])

            return JsonResponse({"status": "success", "message": "Order received successfully!"}, status=201)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    else:
        # Return an error if the request method is not POST
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

@login_required(login_url="/login/")
def order(request):  
    cart = request.session.get('cart', {})
    user_details = request.session.get('user_details', {'phone_number': '', 'uservege_address': ''})

    if not cart:
        return redirect('cart')  # Redirect to cart if no items

    total_price = sum(item['quantity'] * item['price'] for item in cart.values())  # Calculate total price

    # Prepare order data to send to delivery web app
    order_data = {
        "user_id": request.user.id,
        "items": cart,
        "total_price": total_price,
        'user_details': user_details,  # Pass user details to the template
    }

    # Delivery Web App API URL
    DELIVERY_API_URL = settings.DELIVERY_API_URL

    try:
        # Ensure the request is a POST request
        print("Sending order data to:", DELIVERY_API_URL)  # Debugging
        print("Order data:", order_data)  # Debugging
        response = requests.post(DELIVERY_API_URL, json=order_data)
        if response.status_code == 201:
            messages.success(request, "Order sent to delivery!")
        else:
            messages.error(request, f"Failed to send order to delivery. Status code: {response.status_code}")
    except Exception as e:
        messages.error(request, f"Error contacting delivery service: {str(e)}")

    context = {'cart': cart, 'total_price': total_price , 'user_details': user_details}
    return render(request, 'order.html', context)

@login_required(login_url="/login/")
def verify_payment(request):
    payment_id = request.GET.get('payment_id')

    if not payment_id:
        messages.error(request, "Payment failed. Please try again.")
        return redirect('cart')

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        payment = client.payment.fetch(payment_id)
        if payment['status'] == "captured":
            messages.success(request, "Payment successful!")
            return redirect('order')
        else:
            messages.error(request, "Payment verification failed.")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")

    return redirect('order')

@login_required(login_url="/login/")
def receipe_suggestion(request):
    query = request.GET.get('query', '')
    recipes = []

    if query:
        api_url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            recipes = data.get('meals', [])

    return render(request, 'receipe_suggestion.html', {'recipes': recipes, 'query': query})


