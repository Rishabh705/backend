from django.db import models
from django.core.exceptions import ValidationError
import re

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    age = models.IntegerField(null=False)
    phone_number = models.CharField(max_length=15, null=False)
    monthly_salary = models.FloatField(null=False)
    approved_limit = models.FloatField(null=False)

    @property
    def calculate_approved_limit(self):
        # Calculate approved limit based on monthly salary, rounding to the nearest lakh
        return round(self.monthly_salary * 36, -5)

    def clean(self):
        # Age check (18 to 100)
        if self.age < 18 or self.age > 100:
            raise ValidationError('Age must be between 18 and 100.')

        # Salary and limit check (must be positive)
        if self.monthly_salary <= 0:
            raise ValidationError('Monthly salary must be a positive number.')

        # Phone number format check (basic regex for valid phone number)
        if not re.match(r'^\+?\d{10,15}$', self.phone_number):
            raise ValidationError('Phone number must be valid with 10 to 15 digits.')

    def save(self, *args, **kwargs):
        self.clean()  # Ensure data is cleaned before saving
        self.approved_limit = self.calculate_approved_limit  # Calculate and set limit
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'