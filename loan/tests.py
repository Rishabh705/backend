from django.test import TestCase
from django.urls import reverse
from .models import Customer, Loan
from rest_framework import status
from unittest.mock import patch

class LoanEligibilityTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Create a customer for testing with a valid phone number
        cls.customer = Customer.objects.create(
            customer_id='1',
            monthly_salary=117000,
            approved_limit=4200000,
            age=30,  # Valid age value
            phone_number='1234567890',  # Add a valid phone number here (10 digits)
        )

    @patch('loan.views.check_eligibility_view')
    def test_eligibility_approve(self, mock_calculate_credit_score):
        # Mock the calculate_credit_score to return a score > 50
        mock_calculate_credit_score.return_value = 60
        
        response = self.client.post(reverse('check-eligibility'), {
            "customer_id": self.customer.customer_id,
            "loan_amount": 500000,
            "interest_rate": 10.0,
            "tenure": 24
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['loan_approved'])
        self.assertEqual(response.data['corrected_interest_rate'], 10)

    # @patch('./views.py')
    # def test_eligibility_interest_rate_adjustment(self, mock_calculate_credit_score):
    #     # Mock the calculate_credit_score to return a score between 30 and 50
    #     mock_calculate_credit_score.return_value = 40
        
    #     response = self.client.post(reverse('check-eligibility'), {
    #         'customer_id': self.customer.customer_id,
    #         'loan_amount': 50000,
    #         'requested_interest_rate': 8,
    #         'tenure': 24
    #     })

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertTrue(response.data['loan_approved'])
    #     self.assertEqual(response.data['corrected_interest_rate'], 12)  # Adjusted to 12% based on score

    # @patch('./views.py')
    # def test_eligibility_deny_low_credit_score(self, mock_calculate_credit_score):
    #     # Mock the calculate_credit_score to return a score <= 10
    #     mock_calculate_credit_score.return_value = 5
        
    #     response = self.client.post(reverse('check-eligibility'), {
    #         'customer_id': self.customer.customer_id,
    #         'loan_amount': 50000,
    #         'requested_interest_rate': 8,
    #         'tenure': 24
    #     })

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertFalse(response.data['loan_approved'])
    #     self.assertEqual(response.data['corrected_interest_rate'], 8)  # No change to interest rate

    # @patch('./views.py')
    # def test_eligibility_exceeding_approved_limit(self, mock_calculate_credit_score):
    #     # Mock the calculate_credit_score to return a valid score
    #     mock_calculate_credit_score.return_value = 60

    #     # Assuming the customer already has a total loan of 150,000
    #     Loan.objects.create(
    #         customer=self.customer,
    #         loan_amount=150000,
    #         emis_paid_on_time=12,
    #         approval_date='2023-01-01',
    #         end_date='2025-01-01'
    #     )

    #     response = self.client.post(reverse('check-eligibility'), {
    #         'customer_id': self.customer.customer_id,
    #         'loan_amount': 100000,  # Exceeds approved limit (150,000 + 100,000 = 250,000)
    #         'requested_interest_rate': 10,
    #         'tenure': 24
    #     })

    #     self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
    #     self.assertEqual(response.data['error'], 'Customer has exceeded their approved credit limit.')

    # def test_missing_fields(self):
    #     response = self.client.post(reverse('check-eligibility'), {
    #         'customer_id': self.customer.customer_id,
    #         'loan_amount': 50000,
    #         'requested_interest_rate': 10,
    #     })  # Missing tenure
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data['error'], 'Tenure is required.')

    # def test_invalid_customer(self):
    #     response = self.client.post(reverse('check-eligibility'), {
    #         'customer_id': 'INVALID_ID',
    #         'loan_amount': 50000,
    #         'requested_interest_rate': 10,
    #         'tenure': 24
    #     })
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    #     self.assertEqual(response.data['error'], 'Customer not found.')

    # def test_invalid_loan_amount(self):
    #     response = self.client.post(reverse('check-eligibility'), {
    #         'customer_id': self.customer.customer_id,
    #         'loan_amount': -50000,  # Invalid loan amount
    #         'requested_interest_rate': 10,
    #         'tenure': 24
    #     })
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data['error'], 'Loan amount must be greater than 0.')

    # def test_interest_rate_greater_than_100(self):
    #     response = self.client.post(reverse('check-eligibility'), {
    #         'customer_id': self.customer.customer_id,
    #         'loan_amount': 50000,
    #         'requested_interest_rate': 150,  # Invalid interest rate
    #         'tenure': 24
    #     })
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data['error'], 'Requested interest rate cannot be greater than 100.')

