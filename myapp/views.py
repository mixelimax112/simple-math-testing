from django.shortcuts import render
from django.http import HttpResponse


def hello_view(request):
    name = request.GET.get('name', 'Your_name')
    return HttpResponse(f'Hello, {name}')


def home_view(request):
    return render(request, 'home.html')

