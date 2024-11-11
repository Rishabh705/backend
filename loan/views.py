from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Loan
from customer.models import Customer
from datetime import date
from django.db.models import Sum

def calculate_credit_score(customer, loan_amount):
    # Get the customer's past loans
    loans = Loan.objects.filter(customer=customer)
    
    # Loans paid on time (assuming 'emis_paid_on_time' is an integer count of EMIs paid on time)
    paid_on_time = loans.aggregate(total_paid_on_time=Sum('emis_paid_on_time'))['total_paid_on_time'] or 0
    
    # Total number of loans
    total_loans = loans.count()
    
    # Loan activity for the current year
    loan_activity_current_year = loans.filter(approval_date__year=date.today().year).count()
    
    # Total approved loan volume (sum of loan amounts)
    approved_loan_volume = loans.aggregate(total=Sum('loan_amount'))['total'] or 0
    
    credit_score = 0
    
    # Factors for calculating credit score
    credit_score += paid_on_time * 10  # 10 points per loan paid on time
    credit_score += total_loans * 5    # 5 points for each loan taken
    credit_score += loan_activity_current_year * 2  # 2 points for each loan activity in the current year
    credit_score += approved_loan_volume // 100000  # 1 point for every 1 Lakh loan approved

    # Check if the sum of current loans exceeds approved limit
    active_loans = Loan.objects.filter(customer=customer, end_date__gte=date.today())  # Loans that are still active
    total_current_loans = active_loans.aggregate(total=Sum('loan_amount'))['total'] or 0

    if loan_amount + total_current_loans > customer.approved_limit:
        return 0  # Set credit score to 0 if loans exceed approved limit

    return credit_score


def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    # Formula for calculating EMI based on loan amount, interest rate, and tenure
    rate_of_interest = interest_rate / 100 / 12  # Monthly rate
    emi = loan_amount * rate_of_interest * ((1 + rate_of_interest) ** tenure) / (((1 + rate_of_interest) ** tenure) - 1)
    return round(emi, 2)

def check_eligibility(customer_id, loan_amount, requested_interest_rate, tenure):
    # Check if all fields are provided
    if customer_id is None:
        return {"error": "Customer ID is required."}, status.HTTP_400_BAD_REQUEST
    if loan_amount is None:
        return {"error": "Loan amount is required."}, status.HTTP_400_BAD_REQUEST
    if requested_interest_rate is None:
        return {"error": "Interest rate is required."}, status.HTTP_400_BAD_REQUEST
    if tenure is None:
        return {"error": "Tenure is required."}, status.HTTP_400_BAD_REQUEST

    # Validate loan_amount and requested_interest_rate
    try:
        loan_amount = float(loan_amount)
    except ValueError:
        return {"error": "Loan amount must be a valid number."}, status.HTTP_400_BAD_REQUEST

    try:
        requested_interest_rate = float(requested_interest_rate)
    except ValueError:
        return {"error": "Interest rate must be a valid number."}, status.HTTP_400_BAD_REQUEST

    try:
        tenure = int(tenure)
    except ValueError:
        return {"error": "Tenure must be a valid integer."}, status.HTTP_400_BAD_REQUEST

    # Validate loan_amount and requested_interest_rate are greater than 0
    if loan_amount <= 0:
        return {"error": "Loan amount must be greater than 0."}, status.HTTP_400_BAD_REQUEST

    if requested_interest_rate <= 0:
        return {"error": "Interest rate must be greater than 0."}, status.HTTP_400_BAD_REQUEST

    # Validate requested interest rate
    if requested_interest_rate > 100:
        return {"error": "Requested interest rate cannot be greater than 100."}, status.HTTP_400_BAD_REQUEST
    
    # Get the customer object
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return {"error": "Customer not found."}, status.HTTP_404_NOT_FOUND

    # Check if the sum of current loans + requested loan amount exceeds the approved limit
    total_current_loans = Loan.objects.filter(customer=customer, end_date__gte=date.today()).aggregate(total=Sum('loan_amount'))['total'] or 0
    if total_current_loans + loan_amount > customer.approved_limit:
        return {"error": "Customer has exceeded their approved credit limit."}, status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Calculate the credit score
    credit_score = calculate_credit_score(customer, loan_amount)

    # Determine loan approval based on the credit score
    loan_approved = False
    corrected_interest_rate = requested_interest_rate
    if credit_score > 50:
        loan_approved = True
    elif 30 < credit_score <= 50:
        if requested_interest_rate <= 12:
            corrected_interest_rate = 12
        loan_approved = True
    elif 10 < credit_score <= 30:
        if requested_interest_rate <= 16:
            corrected_interest_rate = 16
        loan_approved = True
    else:
        loan_approved = False

    # Check if monthly installments exceed 50% of monthly salary
    if loan_approved:
        monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
        if monthly_installment > (customer.monthly_salary * 0.5):
            return {"error": "Loan cannot be approved as the monthly installment exceeds 50% of monthly salary."}, status.HTTP_422_UNPROCESSABLE_ENTITY
    
    return {
        "customer_id": customer.customer_id,
        "requested_interest_rate": requested_interest_rate,
        "corrected_interest_rate": corrected_interest_rate,
        "loan_approved": loan_approved,
        "monthly_installment": monthly_installment
    }, status.HTTP_200_OK


@api_view(['POST'])
def check_eligibility_view(request):
    if request.method == 'POST':
        # Extract data from the request body
        customer_id = request.data.get('customer_id')
        loan_amount = request.data.get('loan_amount')
        requested_interest_rate = request.data.get('interest_rate')
        tenure = request.data.get('tenure')

        # Call the check_eligibility function to determine eligibility
        result, status_code = check_eligibility(customer_id, loan_amount, requested_interest_rate, tenure)

        # Define a default response structure
        response_data = {
            "customer_id": customer_id,
            "approval": result.get("loan_approved", False),
            "interest_rate": requested_interest_rate if requested_interest_rate else None,
            "corrected_interest_rate": result.get("corrected_interest_rate"),
            "tenure": tenure if tenure else None,
            "monthly_installment": result.get("monthly_installment")
        }

        # Return the response with the appropriate status code
        return Response(response_data, status=status_code)


@api_view(['POST'])
def create_loan_view(request):
    if request.method == 'POST':
        customer_id = request.data.get('customer_id')
        loan_amount = request.data.get('loan_amount')
        requested_interest_rate = request.data.get('interest_rate')
        tenure = request.data.get('tenure')

        eligibility_response, status_code = check_eligibility(customer_id, loan_amount, requested_interest_rate, tenure)

        # If eligibility check fails or loan is not approved, return response data
        if status_code != status.HTTP_200_OK or not eligibility_response.get("loan_approved"):
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": eligibility_response.get("error", "Loan was not approved"),
                "monthly_installment": None
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # Ensure the customer exists
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({
                "error": "Customer not found."
            }, status=status.HTTP_404_NOT_FOUND)

        corrected_interest_rate = eligibility_response.get("corrected_interest_rate")
        monthly_installment = eligibility_response.get("monthly_installment")

        # Create loan record
        try:
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                interest_rate=corrected_interest_rate,
                tenure=tenure,
                monthly_repayment=monthly_installment
            )
        except Exception as e:
            return Response({
                "error": f"Failed to create loan: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Successful loan creation
        response_data = {
            "loan_id": loan.loan_id,
            "customer_id": customer_id,
            "loan_approved": True,
            "message": "Loan was approved successfully",
            "monthly_installment": monthly_installment
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def view_loan_view(request, loan_id):
    # Check if loan_id is provided and valid
    if loan_id is None:
        return Response({"error": "Loan ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Fetch all loans with the given loan_id
        loans = Loan.objects.filter(loan_id=loan_id)
        
        # If no loans found, return an error
        if not loans:
            return Response({"error": "No loans found with the provided Loan ID."}, status=status.HTTP_404_NOT_FOUND)

        # Prepare the response data
        response_data = []
        for loan in loans:
            loan_data = {
                "loan_id": loan.loan_id,
                "customer": {
                    "customer_id": loan.customer.customer_id,
                    "first_name": loan.customer.first_name,
                    "last_name": loan.customer.last_name,
                    "phone_number": loan.customer.phone_number,
                    "age": loan.customer.age
                },
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_repayment,
                "tenure": loan.tenure
            }
            response_data.append(loan_data)
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def view_loans_view(request, customer_id):
    # Check if customer_id is provided and valid
    if customer_id is None:
        return Response({"error": "Customer ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Fetch the customer based on customer_id
        customer = Customer.objects.get(customer_id=customer_id)

        # Fetch all current (active) loans for the customer
        current_loans = Loan.objects.filter(customer=customer, end_date__gte=date.today())

        # If no active loans exist for the customer, return a message
        if not current_loans.exists():
            return Response({"message": "No active loans found for this customer."}, status=status.HTTP_200_OK)

        # Prepare the response data for each loan
        response_data = []
        for loan in current_loans:
            repayments_left = max(loan.tenure - loan.emis_paid_on_time, 0)  # Calculate EMIs left

            response_data.append({
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_repayment,
                "repayments_left": repayments_left
            })

        return Response(response_data, status=status.HTTP_200_OK)
    
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

