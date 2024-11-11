from django.shortcuts import render
from rest_framework.permissions import AllowAny

def home(request):
    return render(request, 'api.html')
    