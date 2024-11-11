from django.urls import path, include
from .views import  home

urlpatterns = [
    path("", home, name="home"),
    path("customer/", include('customer.urls')),
    path("loan/", include('loan.urls')),
]
