# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install the dependencies in the requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your Django app will run on
EXPOSE 8000

# Set the environment variable to prevent Python from writing pyc files
ENV PYTHONUNBUFFERED 1

# Run migrations and start the server
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
