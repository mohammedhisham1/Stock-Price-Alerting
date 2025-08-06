#!/bin/bash
# Docker Setup and Management Script for Stock Price Alerting System

set -e

echo "🐳 Stock Price Alerting System - Docker Management"
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed"
}

# Build images
build_images() {
    print_status "Building Docker images..."
    docker-compose build --no-cache
    print_status "Images built successfully"
}

# Start development environment
start_dev() {
    print_status "Starting development environment..."
    docker-compose -f docker-compose.dev.yml up -d
    print_status "Development environment started"
    print_status "Backend: http://localhost:8000"
    print_status "Database: localhost:5432"
    print_status "Redis: localhost:6379"
}

# Start production environment
start_prod() {
    print_status "Starting production environment..."
    docker-compose up -d
    print_status "Production environment started"
    print_status "Frontend: http://localhost"
    print_status "Backend API: http://localhost:8000"
}

# Stop all services
stop_services() {
    print_status "Stopping all services..."
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    print_status "All services stopped"
}

# Clean up everything
cleanup() {
    print_warning "This will remove all containers, images, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v --rmi all
        docker-compose -f docker-compose.dev.yml down -v --rmi all
        docker system prune -f
        print_status "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Show logs
show_logs() {
    if [ "$2" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml logs -f
    else
        docker-compose logs -f
    fi
}

# Show status
show_status() {
    print_status "Container Status:"
    docker-compose ps
    echo ""
    docker-compose -f docker-compose.dev.yml ps
}

# Run Django management commands
run_django_command() {
    if [ -z "$2" ]; then
        print_error "Please provide a Django command"
        exit 1
    fi
    
    print_status "Running Django command: $2"
    docker-compose exec backend python manage.py $2
}

# Database operations
reset_db() {
    print_warning "This will reset the database and load seed data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Resetting database..."
        docker-compose exec backend python manage.py flush --noinput
        docker-compose exec backend python manage.py migrate
        docker-compose exec backend python manage.py loaddata seed_data_fixed.json
        print_status "Database reset completed"
    else
        print_status "Database reset cancelled"
    fi
}

# Show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build          Build Docker images"
    echo "  dev            Start development environment"
    echo "  prod           Start production environment"
    echo "  stop           Stop all services"
    echo "  cleanup        Remove all containers, images, and volumes"
    echo "  logs [dev]     Show logs (add 'dev' for development environment)"
    echo "  status         Show container status"
    echo "  shell          Open Django shell in backend container"
    echo "  manage <cmd>   Run Django management command"
    echo "  reset-db       Reset database and load seed data"
    echo "  help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev                    # Start development environment"
    echo "  $0 manage migrate         # Run migrations"
    echo "  $0 manage createsuperuser # Create Django superuser"
    echo "  $0 logs dev               # Show development logs"
}

# Main script logic
case "$1" in
    "build")
        check_docker
        build_images
        ;;
    "dev")
        check_docker
        start_dev
        ;;
    "prod")
        check_docker
        start_prod
        ;;
    "stop")
        stop_services
        ;;
    "cleanup")
        cleanup
        ;;
    "logs")
        show_logs $@
        ;;
    "status")
        show_status
        ;;
    "shell")
        docker-compose exec backend python manage.py shell
        ;;
    "manage")
        run_django_command $@
        ;;
    "reset-db")
        reset_db
        ;;
    "help"|"")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
