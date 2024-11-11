#!/bin/bash

# Read the environment variables
DB_NAME=${DB_NAME:-"mydb"}  # Default to 'mydb' if not set
DB_USER=${DB_USER:-"postgres"}  # Default to 'postgres' if not set
DB_PASSWORD=${DB_PASSWORD:-"postgres"}  # Default to 'postgres' if not set

# Replace the placeholders in the SQL file and execute it
envsubst < /docker-entrypoint-initdb.d/init.sql > /app/init.sql
psql -U postgres -f /app/init.sql
