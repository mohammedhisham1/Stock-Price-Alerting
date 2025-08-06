#!/bin/bash

# Quick Setup Script for Stock Price Alerting System
# Run this script to set up the development environment

echo "🚀 Setting up Stock Price Alerting System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
echo "⚙️ Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
else
    echo "✅ .env file already exists."
fi

# Run migrations
echo "🗄️ Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Load seed data
echo "🌱 Loading seed data..."
python manage.py loaddata seed_data.json

# Initialize stocks
echo "📈 Initializing monitored stocks..."
python manage.py init_stocks

# Create superuser (optional)
echo "👤 Creating superuser..."
echo "You can skip this step and create a superuser later with: python manage.py createsuperuser"
python manage.py createsuperuser --noinput --username admin --email admin@example.com || echo "Skipped superuser creation"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🔧 Next steps:"
echo "1. Edit .env file with your API keys and email configuration:"
echo "   - Get a free API key from https://twelvedata.com/"
echo "   - Configure Gmail SMTP settings"
echo ""
echo "2. Start Redis server (required for Celery):"
echo "   - Install Redis: brew install redis (Mac) or apt install redis-server (Ubuntu)"
echo "   - Start Redis: redis-server"
echo ""
echo "3. Start the development server:"
echo "   python manage.py runserver"
echo ""
echo "4. In separate terminals, start Celery worker and beat:"
echo "   celery -A stock_alerting worker -l info"
echo "   celery -A stock_alerting beat -l info"
echo ""
echo "5. Visit http://localhost:8000/admin/ to access Django admin"
echo "6. API documentation is available in API_DOCUMENTATION.md"
echo "7. Test the health endpoint: http://localhost:8000/health/"
echo ""
echo "🎉 Happy coding!"
