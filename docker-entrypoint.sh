#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
done
echo "Database started"

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
if [ "$LOAD_SEED_DATA" = "true" ]; then
    echo "Loading seed data..."
    python manage.py loaddata seed_data_fixed.json || echo "Seed data loading failed or already loaded"
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting application..."
exec "$@"
