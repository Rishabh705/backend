FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev postgresql-client gcc python3-dev

# Copy application files
COPY . /app/

# Copy init.sql and init-db.sh
COPY init.sql /docker-entrypoint-initdb.d/
COPY init-db.sh /docker-entrypoint-initdb.d/

# Make the shell script executable
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Optionally run collectstatic only when needed (comment this if in development)
RUN python manage.py collectstatic --noinput

# Expose port 8000 for Django server
EXPOSE 8000

# Set environment variable to prevent Python from buffering output
ENV PYTHONUNBUFFERED 1

# Default command to run Django migrations, the database initialization script, and the server
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && /docker-entrypoint-initdb.d/init-db.sh && python manage.py runserver 0.0.0.0:8000"]
