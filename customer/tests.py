import json
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Customer

class CustomerRegistrationTestCase(TestCase):
    def setUp(self):
        # Set up the client and initial data
        self.client = APIClient()
        self.url = '/api/customer/register/'

        # Sample valid customer data
        self.valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 30,
            'monthly_salary': 50000,
            'phone_number': '+1234567890'
        }

    def test_successful_registration(self):
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('customer_id', response.data)
        self.assertEqual(response.data['name'], 'John Doe')
        self.assertEqual(response.data['age'], 30)
        self.assertEqual(response.data['monthly_income'], 50000)
        self.assertEqual(response.data['phone_number'], '+1234567890')
        self.assertEqual(response.data['approved_limit'], 1800000)

    def test_missing_first_name(self):
        data = self.valid_data.copy()
        data.pop('first_name')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "First name is required.")

    def test_missing_last_name(self):
        data = self.valid_data.copy()
        data.pop('last_name')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Last name is required.")

    def test_missing_age(self):
        data = self.valid_data.copy()
        data.pop('age')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Age is required.")

    def test_missing_monthly_salary(self):
        data = self.valid_data.copy()
        data.pop('monthly_salary')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Monthly salary is required.")

    def test_missing_phone_number(self):
        data = self.valid_data.copy()
        data.pop('phone_number')
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Phone number is required.")

    def test_invalid_age(self):
        # Test for age less than 18
        invalid_data = self.valid_data.copy()
        invalid_data['age'] = 17
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Age must be between 18 and 100.")

        # Test for age greater than 100
        invalid_data['age'] = 101
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Age must be between 18 and 100.")

    def test_invalid_monthly_salary(self):
        # Test for non-positive monthly income
        invalid_data = self.valid_data.copy()
        invalid_data['monthly_salary'] = -5000
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Monthly salary must be positive.")

        invalid_data['monthly_salary'] = 0
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Monthly salary must be positive.")


    def test_invalid_phone_number(self):
        # Test invalid phone number (not 10-15 digits)
        invalid_data = self.valid_data.copy()
        invalid_data['phone_number'] = '12345'
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Phone number must be valid with 10 to 15 digits.")

        # Test phone number with letters
        invalid_data['phone_number'] = 'abcd123456'
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Phone number must be valid with 10 to 15 digits.")

    def test_phone_number_already_registered(self):
        # Create an existing customer
        Customer.objects.create(
            first_name='Jane',
            last_name='Doe',
            age=28,
            phone_number='+1234567890',
            monthly_salary=40000
        )

        # Try registering a customer with the same phone number
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Phone number already registered.")

    def test_approved_limit_calculation(self):
        valid_data = self.valid_data.copy()
        valid_data['monthly_salary'] = 60000  # Test with a different monthly income
        response = self.client.post(self.url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['approved_limit'], round(valid_data['monthly_salary']*36,-5))  # 60000 * 36
