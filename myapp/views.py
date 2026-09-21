from django.shortcuts import render
from django.http import HttpResponse


def hello_view(request):
    """Простое представление, возвращающее приветственный текст"""
    name = request.GET.get('name', 'Your_name')
    return HttpResponse(f'Hello, {name}')


def home_view(request):
    """Домашняя страница"""
    return render(request, 'home.html')

