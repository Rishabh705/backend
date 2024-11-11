from django.urls import path
from . import views

urlpatterns = [
    path('check-eligibility/', views.check_eligibility_view, name='check-eligibility'),
    path('create-loan/', views.create_loan_view, name='create-loan'),
    path('view-loan/<int:loan_id>/', views.view_loan_view, name='view-loan'),
    path('view-loans/<int:customer_id>/', views.view_loans_view, name='view-loans'),
]
