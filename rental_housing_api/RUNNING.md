# Rental Housing API - Запуск проекта

## ✅ Проект успешно запущен!

### 📋 Доступные URL:

- **API (Listings)**: http://localhost:8000/api/listings/
- **API Documentation (Swagger)**: http://localhost:8000/api/docs/
- **API Schema**: http://localhost:8000/api/schema/
- **Admin Panel**: http://localhost:8000/admin/
- **Reviews**: http://localhost:8000/api/reviews/
- **Bookings**: http://localhost:8000/api/bookings/ (требует авторизацию)
- **Auth Register**: http://localhost:8000/api/auth/register/ (POST)

### 🔐 Доступ к админ-панели:

- **Email**: admin@example.com
- **Password**: admin123
- **URL**: http://localhost:8000/admin/

### 🐳 Управление Docker контейнерами:

```bash
# Запустить проект
docker-compose up -d

# Остановить проект
docker-compose down

# Перезапустить проект
docker-compose restart

# Посмотреть логи
docker-compose logs web
docker-compose logs db

# Пересобрать контейнеры
docker-compose down
docker-compose up --build -d
```

### 🗄️ База данных:

- **Тип**: MySQL 8.0
- **Хост**: localhost (внутри Docker: db)
- **Порт**: 3306
- **База данных**: rental_housing_db
- **Пользователь**: rental_user
- **Пароль**: rental_password

### 📝 Что было исправлено:

1. ✅ Убран `simple_history.middleware` из MIDDLEWARE (библиотека отключена)
2. ✅ Включен `djmoney` обратно в INSTALLED_APPS
3. ✅ Исправлена сериализация MoneyField - используется `price.amount` и `price.currency`
4. ✅ Настроены правильные переменные окружения для Docker
5. ✅ Все контейнеры запущены и работают корректно

### 🚀 Статус сервисов:

- ✅ Web (Django): запущен на порту 8000
- ✅ Database (MySQL): запущен и доступен
- ✅ API эндпоинты: работают
- ✅ Admin панель: доступна

### 📊 Текущие данные:

В базе данных есть 1 тестовый листинг (ID: 1)
