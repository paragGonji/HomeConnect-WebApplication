from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required



# Create your views here.
# receipes page test
@login_required(login_url="/login/")
def receipes(request):

    if request.method == "POST":
        data = request.POST
        receipe_name = data.get('receipe_name')
        receipe_description = data.get('receipe_description') 
        receipe_image = request.FILES.get('receipe_image')

        Receipe.objects.create(
            receipe_name = receipe_name,
            receipe_description = receipe_description ,
            receipe_image = receipe_image,
            )
        return redirect('/receipes/')

    queryset = Receipe.objects.all()
    if request.GET.get('search'):
        queryset=queryset.filter(receipe_name__icontains = request.GET.get('search'))

    context = {'receipe' : queryset} 
    return render(request , 'receipes.html' , context)



# update receipes in food
@login_required(login_url="/login/")
def update_receipe(request, id):
    queryset = Receipe.objects.get(id =id)

    if request.method == "POST" :
        data = request.POST
        receipe_image = request.FILES.get('receipe_image')
        receipe_name = data.get('receipe_name')
        receipe_description = data.get('receipe_description') 

        queryset.receipe_name = receipe_name
        queryset.receipe_description = receipe_description
        if receipe_image :
            queryset.receipe_image = receipe_image

        queryset.save()
        return redirect('/receipes/')
    context = {'receipe' : queryset}
  
    return render(request , 'update_receipe.html' , context)



# Delete receipes in food with button
@login_required(login_url="/login/")
def delete_receipe(request, id):
    queryset = Receipe.objects.get(id =id)
    queryset.delete()
    
    return redirect('/receipes/')

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
            return redirect('/receipes/')
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



