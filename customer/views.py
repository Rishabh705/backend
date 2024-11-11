from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
import re

@api_view(['POST'])
def register_customer(request):
    if request.method == 'POST':
        # Extract data from the request body
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        age = request.data.get('age')
        monthly_salary = request.data.get('monthly_income')
        phone_number = request.data.get('phone_number')


        if first_name is None or first_name == "":
            return Response({"error": "First name is required."}, status=status.HTTP_400_BAD_REQUEST)
        if last_name is None or last_name == "":
            return Response({"error": "Last name is required."}, status=status.HTTP_400_BAD_REQUEST)
        if age is None:
            return Response({"error": "Age is required."}, status=status.HTTP_400_BAD_REQUEST)
        if monthly_salary is None:
            return Response({"error": "Monthly salary is required."}, status=status.HTTP_400_BAD_REQUEST)
        if phone_number is None or phone_number == "":
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
    

        # Validate age and monthly_salary
        try:
            age = int(age)
        except (ValueError, TypeError):
            return Response({"error": "Age must be a valid number."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            monthly_salary = float(monthly_salary)
        except (ValueError, TypeError):
            return Response({"error": "Monthly salary must be a valid number."}, status=status.HTTP_400_BAD_REQUEST)

        # Validation for age (must be between 18 and 100)
        if not (18 <= age <= 100):
            return Response({"error": "Age must be between 18 and 100."}, status=status.HTTP_400_BAD_REQUEST)

        # Validation for monthly income (must be greater than 0)
        if monthly_salary <= 0:
            return Response({"error": "Monthly salary must be positive."}, status=status.HTTP_400_BAD_REQUEST)
        # Check if all required fields are provided
        if not all([first_name, last_name, age, monthly_salary, phone_number]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure first name and last name are valid strings
        if not isinstance(first_name, str) or not isinstance(last_name, str):
            return Response({"error": "First and last names must be valid strings."}, status=status.HTTP_400_BAD_REQUEST)

        # Phone number validation: Ensure it's valid (10 to 15 digits, optionally starting with '+')
        if not re.match(r'^\+?\d{10,15}$', phone_number):
            return Response({"error": "Phone number must be valid with 10 to 15 digits."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not first_name.isalpha():
            return Response({"error": "First name must only contain alphabetic characters."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not last_name.isalpha():
            return Response({"error": "Last name must only contain alphabetic characters."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if phone number already exists in the database
        if Customer.objects.filter(phone_number=phone_number).exists():
            return Response({"error": "Phone number already registered."}, status=status.HTTP_400_BAD_REQUEST)

        # Use try-except block for database interaction
        try:
            # Create the Customer instance and save it
            customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                age=age,
                monthly_salary=monthly_salary,
                phone_number=phone_number
            )
        except Exception as e:
            # Catch any unexpected database errors
            return Response({"error": f"An error occurred while saving the customer: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Prepare the response data
        response_data = {
            "customer_id": customer.customer_id,
            "name": f"{customer.first_name} {customer.last_name}",
            "age": customer.age,
            "monthly_income": customer.monthly_salary,
            "approved_limit": customer.approved_limit,
            "phone_number": customer.phone_number
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
