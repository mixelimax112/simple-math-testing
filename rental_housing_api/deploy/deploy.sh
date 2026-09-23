#!/bin/bash
# Deployment script for Rental Housing API on AWS EC2

set -e

APP_DIR="/opt/rental_housing_api"
COMPOSE_FILE="docker-compose.prod.yml"

echo "🚀 Starting deployment..."

# Navigate to app directory
cd $APP_DIR

# Pull latest changes (if using git)
if [ -d ".git" ]; then
    echo "📥 Pulling latest changes from git..."
    git pull origin main
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file based on .env.production template"
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f $COMPOSE_FILE down

# Remove old images (optional, comment out if you want to keep them)
echo "🧹 Cleaning up old images..."
docker image prune -f

# Build and start containers
echo "🏗️  Building and starting containers..."
docker-compose -f $COMPOSE_FILE up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run migrations
echo "🔄 Running database migrations..."
docker-compose -f $COMPOSE_FILE exec -T web python manage.py migrate

# Collect static files
echo "📦 Collecting static files..."
docker-compose -f $COMPOSE_FILE exec -T web python manage.py collectstatic --noinput

# Check if containers are running
echo "✅ Checking container status..."
docker-compose -f $COMPOSE_FILE ps

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "Your API is now running at:"
echo "  HTTP: http://$(curl -s http://checkip.amazonaws.com)"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose -f $COMPOSE_FILE logs -f"
echo "  Stop services:    docker-compose -f $COMPOSE_FILE down"
echo "  Restart services: docker-compose -f $COMPOSE_FILE restart"
echo "  Create superuser: docker-compose -f $COMPOSE_FILE exec web python manage.py createsuperuser"
