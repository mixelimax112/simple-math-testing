from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('hello/', views.hello_view, name='hello'),
]
