# Credit Approval System

This is a backend application designed to assess a customer's eligibility for a loan based on their credit history and personal data. The system processes customer and loan data using Django and Django Rest Framework. It also incorporates background tasks for processing large datasets efficiently. The project uses PostgreSQL as the database and Docker for containerization.

## Project Overview

The Credit Approval System evaluates customers' loan eligibility and processes new loan applications based on:
- Past loan repayment behavior.
- Loan activity in the current year.
- Current debt and monthly salary.
- Credit score derived from historical data.

The system provides a set of RESTful APIs to:
- Register customers.
- Check loan eligibility.
- Create new loans.
- View loan details.

## Features

- **Customer Registration**: Adds a new customer and calculates the approved credit limit based on their monthly salary.
- **Loan Eligibility Check**: Evaluates the customer's eligibility for a loan based on a credit score and other conditions.
- **Loan Creation**: Processes new loans after checking eligibility.
- **Loan Details**: View loan details for a specific loan or all loans associated with a customer.
- **Data Ingestion**: Import customer and loan data from Excel files using background tasks.

## Setup and Initialization

### Requirements
- Python 3+
- Django 4+
- Django Rest Framework
- PostgreSQL
- Docker

### 1. Setup

**Clone the Repository**:
```
git clone https://github.com/yourusername/credit-approval-system.git
cd credit-approval-system
```

Install Docker: Make sure Docker is installed and running on your system. Follow the instructions for Docker installation.

Build and Run with Docker: Use Docker Compose to build the containers and run the application.

    docker compose up --build

This will start the Django application and PostgreSQL database in separate containers.

Access the Application: The application will be available at http://localhost:8000/.

**Data Ingestion**

The system uses two Excel files:
1. customer_data.xlsx: Contains existing customer data.
2. loan_data.xlsx: Contains historical loan data.

These files will be ingested into the database using background tasks.

**API Endpoints**

1. Register a Customer - /register

    Method: POST

    Request Body:
    ```
    {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "monthly_income": 50000,
        "phone_number": "1234567890"
    }
    ```
    Response Body:

        {
            "customer_id": 1,
            "name": "John Doe",
            "age": 30,
            "monthly_income": 50000,
            "approved_limit": 1800000,
            "phone_number": "1234567890"
        }

2. Check Loan Eligibility - /check-eligibility

    Method: POST

    Request Body:
    ```
    {
        "customer_id": 1,
        "loan_amount": 100000,
        "interest_rate": 8.5,
        "tenure": 24
    }
    ```
    Response Body:

        {
            "customer_id": 1,
            "approval": true,
            "interest_rate": 8.5,
            "corrected_interest_rate": 12.0,
            "tenure": 24,
            "monthly_installment": 5000.00
        }

3. Create Loan - /create-loan

    Method: POST

    Request Body:
    ```
    {
        "customer_id": 1,
        "loan_amount": 100000,
        "interest_rate": 12.0,
        "tenure": 24
    }
    ```

    Response Body:

        {
            "loan_id": 123,
            "loan_approved": true,
            "message": "Loan approved",
            "monthly_installment": 5000.00
        }

4. View Loan Details - /view-loan/{loan_id}

    Method: GET

    Response Body:
    ```
    {
        "loan_id": 123,
        "customer": {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "1234567890",
            "age": 30
        },
        "loan_amount": 100000,
        "interest_rate": 12.0,
        "monthly_installment": 5000.00,
        "tenure": 24
    }
    ```

5. View Loans by Customer - /view-loans/{customer_id}

    Method: GET
    
    Response Body:
    ```
    [
        {
        "loan_id": 123,
        "loan_amount": 100000,
        "interest_rate": 12.0,
        "monthly_installment": 5000.00,
        "repayments_left": 24
        }
    ]
    ```

**Background Workers**

Background tasks are used to process large amounts of data, such as ingesting the customer and loan data from the Excel files. These tasks run asynchronously to avoid blocking the main application process.

**Dockerization**

The entire application and its dependencies are dockerized, ensuring that it can run consistently across different environments. The docker-compose.yml file defines the services for the application, including the Django app and PostgreSQL database.

To run the application in Docker, use the following command:

```docker-compose up --build```

