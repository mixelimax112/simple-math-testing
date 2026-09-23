#!/bin/bash
# Быстрый деплой приложения (запускать после setup)

set -e

APP_DIR="/opt/rental_housing_api"

echo "🚀 Быстрый деплой Rental Housing API..."

# Переход в директорию проекта
cd $APP_DIR

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден! Создаём из шаблона..."
    cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=change-this-to-secure-random-string-minimum-50-characters
ALLOWED_HOSTS=98.84.179.216,localhost

USE_MYSQL=True
DB_NAME=rental_housing_db
DB_USER=rental_user
DB_PASSWORD=rental_password
DB_HOST=db
DB_PORT=3306

CORS_ALLOWED_ORIGINS=http://98.84.179.216
EOF
    echo "⚠️  ВАЖНО: Отредактируйте .env файл перед запуском!"
    echo "    nano .env"
    exit 1
fi

# Остановка старых контейнеров
echo "🛑 Остановка старых контейнеров..."
docker-compose down || true

# Очистка старых образов
echo "🧹 Очистка..."
docker system prune -f

# Сборка и запуск
echo "🏗️  Сборка и запуск контейнеров..."
docker-compose up -d --build

# Ожидание запуска
echo "⏳ Ожидание запуска сервисов..."
sleep 15

# Проверка статуса
echo "✅ Проверка статуса контейнеров..."
docker-compose ps

# Получение IP
EC2_IP=$(curl -s http://checkip.amazonaws.com)

echo ""
echo "🎉 Деплой завершён!"
echo ""
echo "📍 Ваш API доступен по адресу:"
echo "   http://$EC2_IP:8000/api/"
echo ""
echo "📚 Документация API:"
echo "   http://$EC2_IP:8000/api/docs/"
echo ""
echo "🔐 Админ-панель:"
echo "   http://$EC2_IP:8000/admin/"
echo ""
echo "📋 Полезные команды:"
echo "   Логи:              docker-compose logs -f"
echo "   Создать админа:    docker-compose exec web python manage.py createsuperuser"
echo "   Остановить:        docker-compose down"
echo "   Перезапустить:     docker-compose restart"
