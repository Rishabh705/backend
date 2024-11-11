from django.db import models
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from customer.models import Customer 
import random

class Loan(models.Model):
    loan_id = models.IntegerField(null=False)  
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.FloatField(null=False)
    tenure = models.IntegerField(null=False)  # Tenure in months
    interest_rate = models.FloatField(null=False)
    monthly_repayment = models.FloatField(null=False)
    emis_paid_on_time = models.IntegerField(default=0)
    approval_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=False, blank=True)  # Blank is set for it to be auto-calculated

    class Meta:
        unique_together = ('loan_id', 'customer')  # Ensure unique loan_id per customer

    @staticmethod
    def generate_unique_loan_id():
        # Get the highest loan_id in the table
        last_loan = Loan.objects.order_by('-loan_id').first()  # Get the loan with the highest loan_id
        if last_loan:
            new_loan_id = last_loan.loan_id + 1  # Increment the loan_id by 1
        else:
            new_loan_id = 9956  # Start from 9956 if no loans exist yet
        
        return new_loan_id
    
    def clean(self):
        # Loan amount, monthly repayment, and interest rate must be positive
        if self.loan_amount <= 0:
            raise ValidationError('Loan amount must be a positive number.')

        if self.monthly_repayment <= 0:
            raise ValidationError('Monthly repayment must be a positive number.')

        if not (0 <= self.interest_rate <= 50):
            raise ValidationError('Interest rate must be between 0 and 50.')

        # Tenure check (1 to 360 months, equivalent to 1 to 30 years)
        if self.tenure <= 0 or self.tenure > 360:
            raise ValidationError('Tenure must be between 1 and 360 months.')

        # EMIs paid on time should not exceed the tenure
        if self.emis_paid_on_time > self.tenure:
            raise ValidationError('EMIs paid on time cannot exceed the loan tenure.')

        # End date should be later than the approval date
        if self.end_date and self.approval_date and self.end_date <= self.approval_date:
            raise ValidationError('End date must be later than the approval date.')

    def save(self, *args, **kwargs):
        self.clean()  # Ensure data is cleaned before saving
        
        # Ensure approval_date and tenure are set before calculating end_date
        if not self.loan_id:
            self.loan_id = Loan.generate_unique_loan_id()

        # Ensure approval_date is not None and tenure is valid
        if self.approval_date and self.tenure:
            self.end_date = self.approval_date + relativedelta(months=self.tenure)
        else:
            raise ValidationError('Approval date and tenure are required to calculate the end date.')

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Loan {self.loan_id} for {self.customer.first_name} {self.customer.last_name}'
