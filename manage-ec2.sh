#!/bin/bash

# Stock Price Alerting System - Ubuntu EC2 Management Script
# Usage: ./manage-ec2.sh [start|stop|restart|status|logs|update]

PROJECT_DIR="/home/ubuntu/Stock-Price-Alerting"
VENV_PATH="$PROJECT_DIR/venv"

cd $PROJECT_DIR

case "$1" in
    start)
        echo "🚀 Starting Stock Price Alerting System..."
        sudo supervisorctl start stockalerting:*
        sudo systemctl start nginx
        sudo systemctl start redis
        echo "✅ All services started!"
        ;;
    stop)
        echo "🛑 Stopping Stock Price Alerting System..."
        sudo supervisorctl stop stockalerting:*
        sudo systemctl stop nginx
        echo "✅ All services stopped!"
        ;;
    restart)
        echo "🔄 Restarting Stock Price Alerting System..."
        sudo supervisorctl restart stockalerting:*
        sudo systemctl restart nginx
        sudo systemctl restart redis
        echo "✅ All services restarted!"
        ;;
    status)
        echo "📊 Service Status:"
        echo "==================="
        sudo supervisorctl status
        echo ""
        echo "Nginx Status:"
        sudo systemctl status nginx --no-pager -l
        echo ""
        echo "Redis Status:"
        sudo systemctl status redis --no-pager -l
        ;;
    logs)
        echo "📋 Recent Logs:"
        echo "==============="
        echo "Django Logs:"
        sudo tail -n 20 /var/log/supervisor/stockalerting_django.log
        echo ""
        echo "Celery Worker Logs:"
        sudo tail -n 20 /var/log/supervisor/stockalerting_celery.log
        echo ""
        echo "Celery Beat Logs:"
        sudo tail -n 20 /var/log/supervisor/stockalerting_beat.log
        ;;
    update)
        echo "📥 Updating Stock Price Alerting System..."
        git pull origin main
        source $VENV_PATH/bin/activate
        pip install -r requirements.txt
        python manage.py migrate
        python manage.py collectstatic --noinput
        sudo supervisorctl restart stockalerting:*
        echo "✅ Update completed!"
        ;;
    deploy)
        echo "🚀 Running full deployment setup..."
        source $VENV_PATH/bin/activate
        python manage.py migrate
        python manage.py createsuperuser --noinput || echo "Superuser already exists"
        python manage.py collectstatic --noinput
        python manage.py loaddata seed_data_fixed.json || echo "Seed data already loaded"
        sudo supervisorctl reread
        sudo supervisorctl update
        sudo supervisorctl start stockalerting:*
        sudo systemctl restart nginx
        echo "✅ Deployment completed!"
        ;;
    health)
        echo "🏥 Health Check:"
        echo "================"
        curl -s http://localhost:8000/api/health/ | python3 -m json.tool || echo "❌ Django not responding"
        redis-cli ping || echo "❌ Redis not responding"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|update|deploy|health}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all services"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  status  - Show service status"
        echo "  logs    - Show recent logs"
        echo "  update  - Pull latest code and restart"
        echo "  deploy  - Run full deployment setup"
        echo "  health  - Check service health"
        exit 1
        ;;
esac
