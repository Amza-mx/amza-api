#!/bin/sh
set -e

echo "=== Starting Amza API Deployment ==="

# Change to Django project directory
cd /app/src

# Check critical environment variables
echo "Checking environment variables..."
if [ -z "$SECRET_KEY" ]; then
    echo "ERROR: SECRET_KEY is not set!"
    exit 1
fi

if [ -z "$ALLOWED_HOSTS" ]; then
    echo "WARNING: ALLOWED_HOSTS is not set. Using default."
else
    echo "ALLOWED_HOSTS is set to: $ALLOWED_HOSTS"
fi

echo "DEBUG is set to: $DEBUG"
echo "Environment check passed."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || {
    echo "ERROR: Failed to collect static files"
    exit 1
}

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput || {
    echo "ERROR: Failed to run migrations"
    exit 1
}

echo "Migrations completed successfully."

# Start Gunicorn server
echo "Starting Gunicorn server on 0.0.0.0:8000..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
