#!/bin/bash
set -e

# Function to wait for database
wait_for_db() {
    echo "Waiting for database..."
    while ! nc -z ${DB_HOST:-localhost} ${DB_PORT:-5432}; do
        sleep 0.1
    done
    echo "Database started"
}

# Function to run Django setup (only for backend service)
django_setup() {
    # Run migrations
    echo "Applying database migrations..."
    python manage.py migrate --noinput

    # Create superuser if it doesn't exist
    echo "Creating superuser..."
    python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
EOF

    # Load seed data if LOAD_SEED_DATA is set
    
    echo "Loading seed data..."
    python manage.py loaddata seed_data_fixed.json || echo "Seed data loading failed or already loaded"
    

    # Collect static files
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
}

# Wait for database if DB_HOST is set
if [ -n "$DB_HOST" ]; then
    wait_for_db
fi

# Run Django setup only if this is the main backend service
# (not for celery workers)
if [ "$1" = "gunicorn" ] || [ "$1" = "python" -a "$2" = "manage.py" -a "$3" = "runserver" ]; then
    django_setup
fi

echo "Starting application..."
exec "$@"
