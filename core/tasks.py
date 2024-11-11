import logging
from celery import shared_task, chain
import pandas as pd
from customer.models import Customer
from loan.models import Loan
from django.utils.dateparse import parse_date
from datetime import datetime

# Create a logger for this module
logger = logging.getLogger(__name__)


@shared_task
def ingest_customer_data():
    try:
        logger.info("Starting customer data ingestion...")
        df = pd.read_excel('data/customer_data.xlsx')
        for _, row in df.iterrows():
            # Check if the customer already exists to avoid duplicates
            # logger.info('='*100)
            # logger.info(row, _)
            customer, created = Customer.objects.get_or_create(
                first_name=row['First Name'],
                last_name=row['Last Name'],
                age=row['Age'],
                phone_number=str(row['Phone Number']),
                monthly_salary=row['Monthly Salary'],
                approved_limit=row['Approved Limit']
            )
            logger.info(customer)
        logger.info("Customer data ingestion completed.")
    except Exception as e:
        logger.info(e)
        logger.error(
            f"Customer with ID {row['Customer ID']} not found in row: {row}")
        return


@shared_task
def ingest_loan_data(*args, **kwargs):
    try:
        logger.info("Starting loan data ingestion...")
        df = pd.read_excel('data/loan_data.xlsx')
        for _, row in df.iterrows():
            # Add data to the Loan model
            approval_date = row['Date of Approval']
            end_date = row['End Date']

            # Check if these values are datetime objects and convert if needed
            if isinstance(approval_date, pd.Timestamp):
                approval_date = approval_date.date()  # Extract the date part
            else:
                approval_date = datetime.strptime(
                    approval_date, '%d/%m/%Y').date()

            if isinstance(end_date, pd.Timestamp):
                end_date = end_date.date()  # Extract the date part
            else:
                end_date = datetime.strptime(end_date, '%d/%m/%Y').date()

            # Fetch customer from the database
            try:
                customer = Customer.objects.get(customer_id=row['Customer ID'])
            except Customer.DoesNotExist:
                logger.error(
                    f"Customer with ID {row['Customer ID']} not found.")
                continue

            # Try to insert the loan, handle duplicate loan_id with different customers
            try:
                # Create the loan entry
                Loan.objects.create(
                    loan_id=row['Loan ID'],
                    loan_amount=row['Loan Amount'],
                    tenure=row['Tenure'],
                    interest_rate=row['Interest Rate'],
                    monthly_repayment=row['Monthly payment'],
                    emis_paid_on_time=row['EMIs paid on Time'],
                    approval_date=approval_date,
                    end_date=end_date,
                    customer=customer,
                )
                logger.info(
                    f"Loan with ID {row['Loan ID']} successfully created for Customer {row['Customer ID']}.")
            except IntegrityError as e:
                logger.error(
                    f"Error creating loan with ID {row['Loan ID']} for Customer {row['Customer ID']}: {e}")
                continue

        logger.info("Loan data ingestion completed.")
    except Exception as e:
        logger.error(f"Error during loan data ingestion: {e}")


# Chain tasks to ensure customer data is ingested first, then loan data
def start_data_ingestion():
    chain(ingest_customer_data.s(), ingest_loan_data.s())()
