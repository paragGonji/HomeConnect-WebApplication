from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
import razorpay
from requests import request
import requests
from vege.views import decimal_to_float
from .models import DeliveryOrder, DeliveryPerson
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from decimal import Decimal
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from decimal import Decimal, ROUND_DOWN


# Login view for delivery
def delivery_login(request):
    if request.method == "POST":
        delivery_email = request.POST.get('delivery_email')
        delivery_password = request.POST.get('delivery_password')
        try:
            delivery_person = DeliveryPerson.objects.get(delivery_email=delivery_email)
        except DeliveryPerson.DoesNotExist:
            messages.error(request, "Invalid Email")
            return redirect('delivery_login')
        
        if not check_password(delivery_password, delivery_person.delivery_password):
            messages.error(request, "Invalid Password")
            return redirect('delivery_login')
        else:
            request.session['delivery_id'] = delivery_person.id
            request.session['delivery_name'] = delivery_person.delivery_name
            request.session['delivery_image_url'] = (
                delivery_person.delivery_image.url if delivery_person.delivery_image else "/media/delivery/default_image.png"
            )
            messages.success(request, "Login Successful!")
            return redirect('delivery_person')  # Redirect to dashboard or another page
    return render(request, 'delivery_login.html')


# Registration view for delivery
def delivery_register(request):
    if request.method == "POST":
        delivery_name = request.POST.get('delivery_name')
        delivery_email = request.POST.get('delivery_email')
        delivery_contact = request.POST.get('delivery_contact')
        delivery_address = request.POST.get('delivery_address')
        delivery_area = request.POST.get('delivery_area')
        delivery_image = request.FILES.get('delivery_image')
        delivery_password = request.POST.get('delivery_password')
        confirm_password = request.POST.get('confirm_password')
        
        if delivery_password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'delivery_register.html', locals())
        
        if DeliveryPerson.objects.filter(delivery_email=delivery_email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'delivery_register.html', locals())
        
        hashed_password = make_password(delivery_password)
        
        delivery_person = DeliveryPerson.objects.create(
            delivery_name=delivery_name,
            delivery_email=delivery_email,
            delivery_contact=delivery_contact,
            delivery_address=delivery_address,
            delivery_area=delivery_area,
            delivery_image=delivery_image if delivery_image else None,
            delivery_password=hashed_password,
            delivery_status=False  # Use delivery_status instead of is_active
        )
        
        try:
            send_delivery_activation_email(request, delivery_person)
            messages.success(request, "Account created successfully! Check your email to activate your account.")
        except Exception as e:
            messages.error(request, f"Error sending activation email: {str(e)}")
            delivery_person.delete()
            return redirect('delivery_register')
        
        return redirect('delivery_login')
    return render(request, 'delivery_register.html')


# Function to send the activation email
def send_delivery_activation_email(request, delivery_person):
    mail_subject = "Activate your Delivery Account"
    message = render_to_string("template_delivery_activate_account.html", {
        'user': delivery_person,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(delivery_person.pk)),
        'token': account_activation_token.make_token(delivery_person),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[delivery_person.delivery_email])
    email.send()


# Function to activate the delivery account
def activate_delivery(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = DeliveryPerson.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, DeliveryPerson.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.delivery_status = True  # Activate the account
        user.save()
        messages.success(request, "Thank you for confirming your email! You can now log in.")
        return redirect('delivery_login')
    else:
        messages.error(request, "The activation link is invalid!")
        return redirect('delivery_register')


# Delivery dashboard view
def delivery_dashboard(request):
    if request.session.get('delivery_id'):
        delivery_person = get_object_or_404(DeliveryPerson, id=request.session['delivery_id'])
        profile_image_url = (
            delivery_person.delivery_image.url if delivery_person.delivery_image else '/media/delivery/default_image.png'
        )
        return render(request, 'delivery_person.html', {
            'delivery_person': delivery_person,
            'profile_image_url': profile_image_url,
        })
    else:
        return redirect('delivery_login')


def delivery_person(request):
    if request.session.get('delivery_id'):
        # Fetch the delivery person from the database using the session ID
        delivery_person = get_object_or_404(DeliveryPerson, id=request.session['delivery_id'])
        
        # Get the profile image URL or use a default one
        profile_image_url = (
            delivery_person.delivery_image.url if delivery_person.delivery_image else '/media/delivery/default_image.png'
        )

        # Pass the delivery person and profile image URL to the template
        return render(request, 'delivery_person.html', {
            'delivery_person': delivery_person,
            'profile_image_url': profile_image_url,
        })
    else:
        # Redirect to login if no delivery ID is found in session
        return redirect('delivery_login')






# Earnings page (Placeholder)
def delivery_location(request):
    cart = request.session.get('cart', {})
    user_details = request.session.get('user_details', {'phone_number': '', 'uservege_address': ''})

    if not cart:
        messages.info(request, 'Your cart is empty.')

    total_price = sum(decimal_to_float(item['price']) * item['quantity'] for item in cart.values())


    context = {
        'cart': cart,
        'total_price': total_price,
        'user_details': user_details,
    }
    return render(request, 'delivery_location.html', context)





def delivery_order(request):
    cart = request.session.get('cart', {})  # Get cart from session
    user_details = request.session.get('user_details', {})  # Get user details

    # Check if user_details are empty
    if not user_details.get('phone_number') and not user_details.get('uservege_address'):
        user_details = None  # Set to None if no valid data

    # Check if cart is empty and send a message
    if not cart:
        messages.info(request, 'Your cart is empty.')

    # Check if user details are empty and send a message
    if not user_details:
        messages.info(request, 'Waiting for Any Orders')

    # Calculate total price
    total_price = sum(decimal_to_float(item['price']) * item['quantity'] for item in cart.values())

    context = {
        'cart': cart,
        'total_price': total_price,
        'user_details': user_details,
    }

    return render(request, 'delivery_order.html', context)



def delivery_earning(request):
    delivery_id = request.session.get('delivery_id')

    if not delivery_id:
        messages.error(request, "You must be logged in as a delivery person to view earnings.")
        return redirect('delivery_login')

    # Fetch updated delivery person from DB (to get latest total_earnings)
    delivery_person = get_object_or_404(DeliveryPerson, id=delivery_id)
    delivery_person.refresh_from_db()  # Ensure fresh data

    # Fetch completed orders count
    completed_orders = DeliveryOrder.objects.filter(delivery_person=delivery_person, status='delivered')

    context = {
        'delivery_person': delivery_person,
        'completed_orders': completed_orders.count(),
        'total_earnings': delivery_person.total_earnings,  # Now always updated
        'razorpay_key': settings.RAZORPAY_KEY_ID  # Pass Razorpay key to template
    }

    return render(request, 'delivery_earning.html', context)




def delivered_order(request):
    if 'cart' in request.session:
        delivery_id = request.session.get('delivery_id')

        if not delivery_id:
            messages.error(request, "You must be logged in as a delivery person to mark orders as delivered.")
            return redirect('delivery_login')

        # Fetch the delivery person from the session
        delivery_person = get_object_or_404(DeliveryPerson, id=delivery_id)

        # Calculate total earnings (30% of total price)
        cart = request.session.get('cart', {})
        total_price = sum(Decimal(str(item['price'])) * Decimal(item['quantity']) for item in cart.values())
        delivery_earn = (total_price * Decimal("0.30")).quantize(Decimal("0.00"), rounding=ROUND_DOWN)

        # Add earnings to the database
        delivery_person.total_earnings += delivery_earn
        delivery_person.save()

        # Update delivered orders in the database
        DeliveryOrder.objects.filter(delivery_person=delivery_person, status='pending').update(status='delivered')

        # Clear the session properly
        request.session.pop('cart', None)
        request.session.pop('user_details', None)
        request.session.modified = True  # Mark session as modified

        messages.success(request, f"Order delivered! ₹{delivery_earn} added to your earnings.")

    return redirect('delivery_order')



@csrf_exempt
@login_required
def reset_earnings(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request
            data = json.loads(request.body)
            payment_id = data.get('payment_id')

            # Fetch the delivery person from the session
            delivery_id = request.session.get('delivery_id')
            if not delivery_id:
                return JsonResponse({"success": False, "error": "Delivery person not logged in."})

            delivery_person = DeliveryPerson.objects.get(id=delivery_id)

            # Reset total earnings to 0
            delivery_person.total_earnings = Decimal("0.00")
            delivery_person.save()

            # Return success response
            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method."})