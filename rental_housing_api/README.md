# Rental Housing API

Backend для платформы краткосрочной аренды жилья на Django REST Framework.

## Описание

Полнофункциональный REST API для платформы аренды недвижимости с двумя типами пользователей:
- **Арендодатели (landlord)** - публикуют объявления о жилье
- **Арендаторы (tenant)** - ищут, бронируют жилье и оставляют отзывы

### Основные возможности

- JWT аутентификация
- Управление объявлениями с фото и блокировкой дат
- Система бронирования с валидацией пересечений
- Отзывы и рейтинги
- Аналитика просмотров и поисковых запросов
- Мягкое удаление (soft delete)
- История изменений (audit trail)
- Автоматическая OpenAPI документация

## Технологический стек

- **Django 4.2** + **Django REST Framework 3.14**
- **JWT** аутентификация (djangorestframework-simplejwt)
- **MySQL** в продакшене / **SQLite** для локальной разработки
- **django-environ** - конфигурация через переменные окружения
- **django-money** - работа с денежными суммами
- **django-filter** - фильтрация API
- **django-simple-history** - аудит изменений
- **drf-spectacular** - OpenAPI/Swagger документация
- **Docker** + **docker-compose**

## Структура проекта

```
rental_housing_api/
├── config/              # Настройки Django
├── core/               # Общие миксины и утилиты
├── users/              # Пользователи и аутентификация
├── listings/           # Объявления о жилье
├── bookings/           # Бронирования
├── reviews/            # Отзывы
├── analytics/          # Аналитика и статистика
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd rental_housing_api
```

### 2. Настройка окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` под свои нужды:

```env
DEBUG=True
SECRET_KEY=your-secret-key
USE_MYSQL=False  # True для MySQL, False для SQLite
```

### 3. Запуск через Docker

```bash
docker-compose up --build
```

API будет доступен по адресу: http://localhost:8000

### 4. Запуск локально (без Docker)

Создайте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

Примените миграции:

```bash
python manage.py migrate
```

Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

Запустите сервер:

```bash
python manage.py runserver
```

## API Endpoints

### Аутентификация

- `POST /api/auth/register/` - Регистрация
- `POST /api/auth/login/` - Получение JWT токена
- `POST /api/auth/token/refresh/` - Обновление токена
- `GET /api/auth/users/me/` - Профиль текущего пользователя
- `PUT /api/auth/users/update_profile/` - Обновление профиля
- `DELETE /api/auth/users/delete_account/` - Удаление аккаунта (soft delete)

### Объявления

- `GET /api/listings/` - Список объявлений (с фильтрами)
- `POST /api/listings/` - Создать объявление (только landlord)
- `GET /api/listings/{id}/` - Детали объявления
- `PUT /api/listings/{id}/` - Обновить объявление
- `DELETE /api/listings/{id}/` - Удалить объявление (soft delete)
- `GET /api/listings/my_listings/` - Мои объявления (landlord)
- `POST /api/listings/{id}/upload_photo/` - Загрузить фото
- `POST /api/listings/{id}/block_dates/` - Заблокировать даты

**Фильтры:**
- `?city=Kiev` - по городу
- `?housing_type=apartment` - по типу жилья
- `?min_price=500&max_price=2000` - по цене
- `?min_guests=2` - минимум гостей
- `?search=центр` - поиск по тексту

### Бронирования

- `GET /api/bookings/` - Список бронирований
- `POST /api/bookings/` - Создать бронирование (только tenant)
- `GET /api/bookings/{id}/` - Детали бронирования
- `POST /api/bookings/{id}/update_status/` - Изменить статус
- `GET /api/bookings/my_bookings/` - Мои бронирования (tenant)
- `GET /api/bookings/landlord_bookings/` - Бронирования моих объявлений (landlord)

**Статусы бронирования:**
- `pending` - ожидает подтверждения
- `confirmed` - подтверждено
- `completed` - завершено
- `cancelled` - отменено
- `rejected` - отклонено
- `expired` - истекло

### Отзывы

- `GET /api/reviews/` - Список отзывов
- `POST /api/reviews/` - Создать отзыв (только для completed бронирований)
- `GET /api/reviews/{id}/` - Детали отзыва
- `PUT /api/reviews/{id}/` - Обновить отзыв
- `DELETE /api/reviews/{id}/` - Удалить отзыв
- `GET /api/reviews/my_reviews/` - Мои отзывы
- `GET /api/reviews/?listing={id}` - Отзывы по объявлению

### Аналитика

- `GET /api/analytics/popular_listings/?days=30` - Популярные объявления
- `GET /api/analytics/popular_searches/?days=30` - Популярные поиски
- `GET /api/analytics/listing_stats/?listing_id={id}&days=30` - Статистика объявления
- `POST /api/analytics/log_search/` - Логирование поискового запроса

## Документация API

После запуска сервера доступны:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Модели данных

### User
- Email как логин (вместо username)
- Роли: `tenant` (арендатор), `landlord` (арендодатель)
- Поле `is_landlord` автоматически вычисляется из `role`
- Soft delete

### Listing
- Владелец (FK на User с защитой от удаления)
- Цена с валютой (django-money)
- Типы жилья: apartment, house, studio
- Фото с порядком отображения
- Заблокированные даты

### Booking
- Валидация: даты, количество гостей, пересечения
- Автоматический расчет стоимости
- Защита от пересечений на уровне БД (constraints)
- Максимум 30 ночей
- Soft delete

### Review
- OneToOne связь с Booking
- Рейтинг от 1 до 5
- Только для completed бронирований
- Один отзыв на объявление от одного пользователя

## Переключение БД

### Для локальной разработки (SQLite)

В `.env`:
```env
USE_MYSQL=False
```

### Для продакшена (MySQL)

В `.env`:
```env
USE_MYSQL=True
DB_NAME=rental_housing
DB_USER=root
DB_PASSWORD=password
DB_HOST=db
DB_PORT=3306
```

## Деплой на AWS EC2

### 1. Подготовка сервера

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Клонирование и настройка

```bash
git clone <repository-url>
cd rental_housing_api

# Создание .env
cp .env.example .env
nano .env  # Настройка переменных
```

### 3. Запуск

```bash
docker-compose up -d
```

### 4. Миграции и суперпользователь

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Безопасность

- JWT токены с ротацией
- Валидация на уровне сериализаторов и моделей
- Permissions на уровне объектов
- Защита от SQL-инъекций (ORM)
- CORS настройки
- Секретные данные в переменных окружения

## Разработка

### Создание миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### Запуск тестов

```bash
python manage.py test
```

### Администрирование

Админка доступна по адресу: http://localhost:8000/admin/

## Лицензия

MIT
