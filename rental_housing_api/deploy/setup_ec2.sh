#!/bin/bash
# Setup script for AWS EC2 Ubuntu instance

set -e

echo "🚀 Starting EC2 setup for Rental Housing API..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
echo "📥 Installing Git..."
sudo apt-get install -y git

# Create app directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/rental_housing_api
sudo chown $USER:$USER /opt/rental_housing_api

# Install nginx (optional, if not using docker nginx)
echo "🌐 Installing Nginx..."
sudo apt-get install -y nginx

# Setup firewall
echo "🔒 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Install certbot for SSL (optional)
echo "🔐 Installing Certbot for SSL..."
sudo apt-get install -y certbot python3-certbot-nginx

echo "✅ EC2 setup completed!"
echo ""
echo "Next steps:"
echo "1. Clone your repository to /opt/rental_housing_api"
echo "2. Create .env file with production settings"
echo "3. Run deploy.sh to start the application"
echo ""
echo "⚠️  IMPORTANT: Log out and log back in for Docker permissions to take effect!"
