from decimal import Decimal
import json
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token  # Custom token class
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .models import KitchenInfo, KitchenDish
from django.views.decorators.csrf import csrf_exempt

def kitchen_login(request):
    if request.method == "POST":
        kitchen_email = request.POST.get('kitchen_email')
        kitchen_password = request.POST.get('kitchen_password')
        try:
            kitchen = KitchenInfo.objects.get(kitchen_email=kitchen_email)
        except KitchenInfo.DoesNotExist:
            messages.error(request, "Invalid Email")
            return redirect('kitchen_login')
        # Check if the entered password matches the stored hashed password
        if not check_password(kitchen_password, kitchen.kitchen_password):
            messages.error(request, "Invalid Password")
            return redirect('kitchen_login')
        else:
            # Store kitchen ID in session after successful login
            request.session['kitchen_id'] = kitchen.id
            messages.success(request, "Login Successful!")
            return redirect('personal_kitchen')
    return render(request, 'kitchen_login.html')

def kitchen_register(request):
    if request.method == "POST":
        # Extract data from the form
        kitchen_name = request.POST.get('kitchen_name')
        kitchen_email = request.POST.get('kitchen_email')
        kitchen_description = request.POST.get('kitchen_description')
        kitchen_address = request.POST.get('kitchen_address')
        kitchen_place = request.POST.get('kitchen_place')
        kitchen_image = request.FILES.get('kitchen_image')  # Handle file upload
        kitchen_password = request.POST.get('kitchen_password')
        confirm_password = request.POST.get('confirm_password')
        # Check if passwords match
        if kitchen_password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'kitchen_register.html', {'kitchen_name': kitchen_name, 'kitchen_email': kitchen_email, 'kitchen_description': kitchen_description, 'kitchen_address': kitchen_address, 'kitchen_place': kitchen_place, 'kitchen_image': kitchen_image})  # Render the same page with entered data
        # Check if the email is already registered
        if KitchenInfo.objects.filter(kitchen_email=kitchen_email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'kitchen_register.html', {'kitchen_name': kitchen_name, 'kitchen_email': kitchen_email, 'kitchen_description': kitchen_description, 'kitchen_address': kitchen_address, 'kitchen_place': kitchen_place, 'kitchen_image': kitchen_image})  # Render the same page with entered data
        # Hash the password before saving
        hashed_password = make_password(kitchen_password)
        # Create the KitchenInfo object with hashed password
        kitchen = KitchenInfo.objects.create(
            kitchen_email=kitchen_email,
            kitchen_name=kitchen_name,
            kitchen_description=kitchen_description,
            kitchen_address=kitchen_address,
            kitchen_place=kitchen_place,
            kitchen_image=kitchen_image if kitchen_image else None,  # Optional image
            kitchen_password=hashed_password,  # Store hashed password
        )
        kitchen.is_active = False  # Set the account to inactive initially
        kitchen.save()
        # Send activation email
        try:
            send_activation_email(request, kitchen)
            messages.success(request, "Account created successfully! Please check your email to activate your account.")
        except Exception as e:
            messages.error(request, f"Error sending activation email: {str(e)}")
            kitchen.delete()  # Roll back user creation if email fails
            return redirect(reverse('kitchen_register'))
        return redirect(reverse('kitchen_login'))  # Redirect to login page after successful registration
    return render(request, 'kitchen_register.html')

def send_activation_email(request, kitchen):
    mail_subject = "Activate your Kitchen Account"
    message = render_to_string("template_activate_account.html", {
        'user': kitchen.kitchen_name,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(kitchen.pk)),
        'token': account_activation_token.make_token(kitchen),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[kitchen.kitchen_email])
    email.send()

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = KitchenInfo.objects.get(pk=uid)  # Replace 'User' with your custom user model if needed
    except (TypeError, ValueError, OverflowError, KitchenInfo.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for confirming your email! You can now log in.")
        return redirect('kitchen_login')  # Update the redirect URL if needed
    else:
        messages.error(request, "The activation link is invalid!")
        return redirect('kitchen_register')

def dashboard(request):
    if request.session.get('kitchen_id'):
        kitchen_info = KitchenInfo.objects.filter(id=request.session['kitchen_id']).first()
        kitchen_image_url = kitchen_info.kitchen_image.url if kitchen_info and kitchen_info.kitchen_image else '/media/kitchen/default_image.png'
        return render(request, 'personal_kitchen.html', {'kitchen_image_url': kitchen_image_url})
    else:
        return redirect('kitchen_login')

def personal_kitchen(request):
    # Check if the user is logged in
    if request.session.get('kitchen_id'):
        # Retrieve the logged-in kitchen's information
        kitchen_info = KitchenInfo.objects.filter(id=request.session['kitchen_id']).first()
        kitchen_image_url = kitchen_info.kitchen_image.url if kitchen_info and kitchen_info.kitchen_image else '/media/kitchen/default_image.png'
        return render(request, 'personal_kitchen.html', {
            'kitchen_info': kitchen_info,
            'kitchen_image_url': kitchen_image_url,
        })
    else:
        # Redirect to login if not logged in
        return redirect('kitchen_login')

def kitchen_menu(request):
    if not request.session.get('kitchen_id'):
        return redirect('kitchen_login')

    kitchen = get_object_or_404(KitchenInfo, id=request.session['kitchen_id'])

    if request.method == "POST":
        dish_name = request.POST.get('dish_name')
        dish_description = request.POST.get('dish_description')
        dish_price = request.POST.get('dish_price')
        preparation_time = request.POST.get('preparation_time')
        dish_image = request.FILES.get('dish_image')
        is_available = request.POST.get('is_available')   # Get the availability status from the form

        KitchenDish.objects.create(
            kitchen=kitchen,
            dish_name=dish_name,
            dish_description=dish_description,
            dish_price=dish_price,
            preparation_time=preparation_time,
            dish_image=dish_image if dish_image else None,
            is_available=is_available  # Save availability status
        )
        messages.success(request, "Dish added successfully!")
        return redirect('kitchen_menu')

    queryset = KitchenDish.objects.filter(kitchen=kitchen)  # Only available dishes

    search_query = request.GET.get('search')
    if search_query:
        queryset = queryset.filter(dish_name__icontains=search_query)

    # Add kitchen_image_url to the context
    kitchen_image_url = kitchen.kitchen_image.url if kitchen.kitchen_image else '/media/kitchen/default_image.png'

    context = {
        'dishes': queryset,
        'kitchen_image_url': kitchen_image_url,  # Pass the kitchen image URL to the template
    }
    return render(request, 'kitchen_menu.html', context)

def delete_dish(request, dish_id):
    if not request.session.get('kitchen_id'):
        return redirect('kitchen_login')

    kitchen = get_object_or_404(KitchenInfo, id=request.session['kitchen_id'])
    dish = get_object_or_404(KitchenDish, id=dish_id, kitchen=kitchen)
    dish.delete()
    messages.success(request, "Dish deleted successfully!")
    return redirect('kitchen_menu')

def update_dish(request):
    if request.method == "POST":
        dish_id = request.POST.get('dish_id')
        dish = get_object_or_404(KitchenDish, id=dish_id)

        dish.dish_name = request.POST.get('dish_name')
        dish.dish_description = request.POST.get('dish_description')
        dish.dish_price = request.POST.get('dish_price')
        dish.preparation_time = request.POST.get('preparation_time')

        if 'dish_image' in request.FILES:
            dish.dish_image = request.FILES['dish_image']

        dish.save()
        return JsonResponse({'message': 'Dish updated successfully!'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def add_dish(request):
    if not request.session.get('kitchen_id'):
        return redirect('kitchen_login')

    kitchen = get_object_or_404(KitchenInfo, id=request.session['kitchen_id'])

    if request.method == 'POST':
        dish_name = request.POST.get('dish_name')
        dish_description = request.POST.get('dish_description')
        dish_price = request.POST.get('dish_price')
        preparation_time = request.POST.get('preparation_time')
        dish_image = request.FILES.get('dish_image')

        # Create the dish and associate it with the logged-in kitchen
        KitchenDish.objects.create(
            kitchen=kitchen,  # Associate the dish with the logged-in kitchen
            dish_name=dish_name,
            dish_description=dish_description,
            dish_price=dish_price,
            preparation_time=preparation_time,
            dish_image=dish_image if dish_image else None,
        )

        messages.success(request, "Dish added successfully!")
        return redirect('kitchen_menu')

    return render(request, 'kitchen_menu.html')

def toggle_availability(request):
    if request.method == "POST" and request.session.get('kitchen_id'):
        dish_id = request.POST.get('dish_id')
        try:
            dish = KitchenDish.objects.get(id=dish_id, kitchen__id=request.session['kitchen_id'])
            dish.is_available = not dish.is_available  # Toggle the availability
            dish.save()
            return JsonResponse({'success': True, 'is_available': dish.is_available})
        except KitchenDish.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Dish not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


from decimal import Decimal
from django.shortcuts import render, redirect
from .models import KitchenInfo

def kitchen_earning(request):
    if request.session.get('kitchen_id'):
        kitchen = KitchenInfo.objects.get(id=request.session['kitchen_id'])
        kitchen_image_url = kitchen.kitchen_image.url if kitchen.kitchen_image else '/media/kitchen/default_image.png'

        cart = request.session.get('cart', {})
        total_price = sum(Decimal(str(item['price'])) * Decimal(item['quantity']) for item in cart.values())

        # Calculate 50% of total price
        kitchen_earning = total_price * Decimal('0.50')

        # Update and save kitchen earnings
        kitchen.kitchen_earning += kitchen_earning
        kitchen.save()

        return render(request, 'kitchen_earning.html', {
            'kitchen': kitchen,  # Pass the kitchen object here
            'kitchen_image_url': kitchen_image_url,
            'total_price': total_price,  
            'kitchen_earning': kitchen.kitchen_earning,  # Pass updated earnings to template
            'razorpay_key': settings.RAZORPAY_KEY_ID ,
        })
    else:
        return redirect('kitchen_login')


@csrf_exempt
def reset_kitchenearnings(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payment_id = data.get('payment_id')

            kitchen_id = request.session.get('kitchen_id')
            if not kitchen_id:
                return JsonResponse({"success": False, "error": "Kitchen not logged in."})

            kitchen = KitchenInfo.objects.get(id=kitchen_id)

            # Reset kitchen earnings to 0
            kitchen.kitchen_earning = Decimal("0.00")
            kitchen.save()

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method."})