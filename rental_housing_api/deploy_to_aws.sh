#!/bin/bash
# Полный автоматический деплой на Amazon Linux EC2

set -e

echo "🚀 Начинаем автоматический деплой на AWS EC2..."

# Проверка, что запущено на Amazon Linux
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "📋 Обнаружена ОС: $NAME"
fi

# 1. Обновление системы и установка необходимых пакетов
echo "📦 Обновление системы..."
sudo yum update -y

# 2. Установка Docker
echo "🐳 Установка Docker..."
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# 3. Установка Docker Compose
echo "🔧 Установка Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Установка Git
echo "📥 Установка Git..."
sudo yum install -y git

# 5. Настройка firewall
echo "🔒 Настройка firewall..."
sudo yum install -y firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

echo "✅ Базовая настройка сервера завершена!"
echo ""
echo "⚠️  ВАЖНО: Выполните команду для применения прав Docker:"
echo "    exit"
echo "    ssh -i your-key.pem ec2-user@your-ip"
echo ""
echo "Затем перейдите в папку проекта и выполните:"
echo "    docker-compose up -d --build"
