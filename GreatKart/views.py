from django.shortcuts import render
from django.http import HttpResponse    
from store.models import product

def home(request):
    products=product.objects.all().filter(is_available=True)
    context={
        'products':products,
    }
    return render(request, 'home.html' , context)