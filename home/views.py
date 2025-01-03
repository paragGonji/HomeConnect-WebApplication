from django.shortcuts import render

from django.http import HttpResponse

def home(request):

    peoples = [
        {'Name' : 'parag' , 'age' : 20},
        {'Name' : 'Hritik' , 'age' : 26},
        {'Name' : 'Jatin' , 'age' : 15},
        {'Name' : 'sahil' , 'age' : 21},
        {'Name' : 'pranav' , 'age' : 60}
    ]

    vegetables = ['Pumpkin', 'Tomato', 'potato']

    return render(request , "home/index.html" , context={'page' : 'Django Practice' ,'peoples' : peoples, 'vegetables' : vegetables})


def about(request):
    context = {'page' : 'about'}
    return render(request , "home/about.html", context)




def contact(request):
    context = {'page' : 'context'}
    return render(request , "home/contact.html", context)




def second_page(request):
    return HttpResponse("<h1>Hey this is second page!!!")