# Документация проекта Rental Housing API

## 📋 Описание проекта

**Rental Housing API** - это backend-система для платформы краткосрочной аренды жилья (аналог Airbnb). Проект разработан на Django REST Framework с использованием MySQL в качестве базы данных.

## 🏗️ Архитектура проекта

### Структура приложений

Проект разделен на несколько Django-приложений по принципу модульности:

```
rental_housing_api/
├── config/              # Основные настройки проекта
├── core/                # Базовые классы и утилиты
├── users/               # Управление пользователями
├── listings/            # Объявления о жилье
├── bookings/            # Бронирования
├── reviews/             # Отзывы
└── analytics/           # Аналитика и статистика
```

---

## 📁 Детальное описание модулей

### 1. **config/** - Конфигурация проекта

**Местоположение**: `rental_housing_api/config/`

#### `settings.py` - Основные настройки
**Путь**: `config/settings.py`

**Ключевые настройки:**

- **База данных** (строки 77-98):
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': 'rental_housing_db',
          'USER': 'rental_user',
          'PASSWORD': 'rental_password',
          'HOST': 'db',  # имя Docker контейнера
      }
  }
  ```

- **REST Framework** (строки 133-148):
  - JWT авторизация через `rest_framework_simplejwt`
  - Пагинация по 20 элементов
  - Фильтрация через `django_filters`

- **CORS настройки** (строки 167-172):
  - Разрешены запросы с localhost:3000 (для фронтенда)

- **Мультивалютность** (строки 174-176):
  - Поддержка USD, EUR, UAH

#### `urls.py` - Маршрутизация API
**Путь**: `config/urls.py`

**Структура URL** (строки 23-35):
```python
urlpatterns = [
    path('admin/', admin.site.urls),                    # Админ-панель
    path('api/auth/', include('users.urls')),           # Авторизация
    path('api/', include('listings.urls')),             # Объявления
    path('api/', include('bookings.urls')),             # Бронирования
    path('api/', include('reviews.urls')),              # Отзывы
    path('api/', include('analytics.urls')),            # Аналитика
    path('api/docs/', SpectacularSwaggerView...),       # Swagger документация
]
```

---

### 2. **core/** - Базовые классы

**Местоположение**: `rental_housing_api/core/`

#### `models.py` - Базовые миксины
**Путь**: `core/models.py`

**Реализованные паттерны:**

1. **TimestampedMixin** (строки 4-10):
   - Автоматические поля `created_at` и `updated_at`
   - Используется во всех моделях для отслеживания времени создания/изменения

2. **SoftDeleteMixin** (строки 13-18):
   - Мягкое удаление записей (помечает `deleted_at` вместо физического удаления)
   - Позволяет восстанавливать удаленные данные

3. **SoftDeleteManager** (строки 21-25):
   - Менеджер для автоматической фильтрации удаленных записей
   - `objects.all()` возвращает только неудаленные записи

#### `permissions.py` - Права доступа
**Путь**: `core/permissions.py`

**Кастомные разрешения:**

1. **IsOwnerOrReadOnly** (строки 4-11):
   - Только владелец может редактировать/удалять свои записи
   - Остальные могут только читать

2. **IsLandlord** (строки 14-16):
   - Только пользователи с ролью 'landlord' могут создавать объявления

---

### 3. **users/** - Пользователи и авторизация

**Местоположение**: `rental_housing_api/users/`

#### `models.py` - Модель пользователя
**Путь**: `users/models.py`

**Кастомная модель User** (строки 28-69):

```python
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('guest', 'Гость'),
        ('landlord', 'Владелец жилья'),
        ('admin', 'Администратор'),
    ]
    
    email = models.EmailField(unique=True)  # Email как логин
    name = models.CharField(max_length=100)
    role = models.CharField(choices=ROLE_CHOICES, default='guest')
    phone = models.CharField(max_length=20, blank=True)
```

**Особенности:**
- Авторизация по email (не username)
- Три роли: гость, владелец, админ
- Интеграция с JWT токенами

#### `serializers.py` - Сериализаторы
**Путь**: `users/serializers.py`

**Основные сериализаторы:**

1. **UserRegistrationSerializer** (строки 6-23):
   - Регистрация новых пользователей
   - Автоматическое хеширование паролей

2. **UserSerializer** (строки 26-32):
   - Отображение профиля пользователя
   - Скрывает пароль

#### `views.py` - API эндпоинты
**Путь**: `users/views.py`

**Эндпоинты:**
- `POST /api/auth/register/` - Регистрация
- `POST /api/auth/login/` - Получение JWT токена
- `POST /api/auth/refresh/` - Обновление токена
- `GET /api/auth/profile/` - Получение профиля

---

### 4. **listings/** - Объявления о жилье

**Местоположение**: `rental_housing_api/listings/`

#### `models.py` - Модели
**Путь**: `listings/models.py`

**1. Listing** (строки 9-58):
```python
class Listing(TimestampedMixin, SoftDeleteMixin):
    owner = ForeignKey(User)              # Владелец объявления
    title = CharField(max_length=255)      # Название
    description = TextField()              # Описание
    city = CharField(max_length=100)       # Город
    district = CharField(max_length=100)   # Район
    price = MoneyField()                   # Цена (с валютой)
    rooms_count = PositiveIntegerField()   # Количество комнат
    housing_type = CharField(              # Тип жилья
        choices=['apartment', 'house', 'studio']
    )
    max_guests = PositiveIntegerField()    # Максимум гостей
    is_active = BooleanField()             # Активно/неактивно
```

**2. ListingPhoto** (строки 60-78):
- Фотографии объявлений
- Поле `order` для сортировки
- Связь OneToMany с Listing

**3. BlockedDate** (строки 80-104):
- Заблокированные даты (недоступные для бронирования)
- Валидация: конец > начала

#### `serializers.py` - Сериализаторы
**Путь**: `listings/serializers.py`

**Основные сериализаторы:**

1. **ListingListSerializer** (строки 61-86):
   - Для списка объявлений
   - Включает первое фото и средний рейтинг

2. **ListingSerializer** (строки 29-44):
   - Полная информация об объявлении
   - Включает все фото и заблокированные даты

3. **ListingCreateSerializer** (строки 47-58):
   - Создание нового объявления
   - Автоматически связывает с текущим пользователем

#### `views.py` - ViewSets
**Путь**: `listings/views.py`

**ListingViewSet** (строки 16-89):

**Основные методы:**

- `list()` - Список объявлений с фильтрацией
- `retrieve()` - Детали объявления + запись просмотра в аналитику
- `create()` - Создание объявления (только landlord)
- `update()` / `delete()` - Редактирование/удаление (только владелец)

**Фильтрация** (строки 19-23):
```python
filterset_fields = ['city', 'district', 'housing_type', 'rooms_count']
search_fields = ['title', 'description', 'city', 'district']
ordering_fields = ['price', 'created_at', 'rooms_count']
```

**Кастомные эндпоинты** (строки 68-88):
- `GET /api/listings/my_listings/` - Мои объявления
- `POST /api/listings/{id}/upload_photo/` - Загрузка фото
- `POST /api/listings/{id}/block_dates/` - Блокировка дат

#### `admin.py` - Админ-панель
**Путь**: `listings/admin.py`

**ListingAdmin** (строки 6-38):
- Встроенное редактирование фото и дат
- Фильтры по городу, типу жилья, статусу
- Поиск по названию, городу, району

---

### 5. **bookings/** - Бронирования

**Местоположение**: `rental_housing_api/bookings/`

#### `models.py` - Модель бронирования
**Путь**: `bookings/models.py`

**Booking** (строки 8-67):
```python
class Booking(TimestampedMixin):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    ]
    
    listing = ForeignKey(Listing)      # Объявление
    guest = ForeignKey(User)           # Гость
    check_in = DateField()             # Дата заезда
    check_out = DateField()            # Дата выезда
    guests_count = PositiveIntegerField()  # Количество гостей
    total_price = MoneyField()         # Общая стоимость
    status = CharField(choices=STATUS_CHOICES)
```

**Методы модели:**

- `calculate_total_price()` (строки 44-47): Автоматический расчет стоимости
- `clean()` (строки 49-67): Валидация дат и доступности

#### `serializers.py` - Сериализаторы
**Путь**: `bookings/serializers.py`

**BookingSerializer** (строки 8-56):
- Автоматический расчет `total_price`
- Валидация пересечений с другими бронированиями
- Проверка заблокированных дат

#### `views.py` - ViewSets
**Путь**: `bookings/views.py`

**BookingViewSet** (строки 11-59):

**Эндпоинты:**
- `GET /api/bookings/` - Список бронирований пользователя
- `POST /api/bookings/` - Создание бронирования
- `POST /api/bookings/{id}/confirm/` - Подтверждение (только владелец)
- `POST /api/bookings/{id}/cancel/` - Отмена

---

### 6. **reviews/** - Отзывы

**Местоположение**: `rental_housing_api/reviews/`

#### `models.py` - Модель отзыва
**Путь**: `reviews/models.py`

**Review** (строки 7-40):
```python
class Review(TimestampedMixin):
    booking = OneToOneField(Booking)       # Один отзыв на бронирование
    rating = PositiveIntegerField(         # Оценка 1-5
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = TextField()                  # Текст отзыва
    landlord_reply = TextField(blank=True) # Ответ владельца
```

**Валидация** (строки 28-40):
- Можно оставить отзыв только после завершения бронирования
- Один отзыв на одно бронирование

#### `views.py` - ViewSets
**Путь**: `reviews/views.py`

**ReviewViewSet** (строки 10-47):

**Эндпоинты:**
- `GET /api/reviews/` - Список отзывов
- `POST /api/reviews/` - Создание отзыва (только гость после завершения)
- `POST /api/reviews/{id}/reply/` - Ответ владельца

---

### 7. **analytics/** - Аналитика

**Местоположение**: `rental_housing_api/analytics/`

#### `models.py` - Модели для аналитики
**Путь**: `analytics/models.py`

**1. SearchQuery** (строки 7-32):
- Хранит историю поисковых запросов
- Параметры поиска в JSONField
- Отслеживание IP адресов

**2. ListingView** (строки 35-62):
- Фиксирует просмотры объявлений
- Связь с пользователем (если авторизован)
- Используется для статистики популярности

#### `views.py` - Аналитические эндпоинты
**Путь**: `analytics/views.py`

**AnalyticsViewSet** (строки 12-66):

**Эндпоинты:**

1. `GET /api/analytics/popular_listings/` (строки 17-26):
   - Топ-10 популярных объявлений по просмотрам

2. `GET /api/analytics/listing_stats/` (строки 28-47):
   - Статистика по объявлениям владельца
   - Количество бронирований, просмотров, средний рейтинг

3. `POST /api/analytics/log_search/` (строки 49-58):
   - Логирование поисковых запросов

---

## 🔐 Система авторизации

### JWT токены
**Реализация**: `rest_framework_simplejwt`

**Настройки** (`config/settings.py`, строки 150-157):
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),      # Токен живет 1 час
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # Обновление 7 дней
    'ROTATE_REFRESH_TOKENS': True,                    # Ротация токенов
}
```

**Процесс авторизации:**
1. `POST /api/auth/login/` → получение access + refresh токенов
2. Добавление заголовка: `Authorization: Bearer <access_token>`
3. При истечении access → `POST /api/auth/refresh/` для обновления

### Права доступа

**Уровни доступа:**
- **IsAuthenticatedOrReadOnly**: Чтение доступно всем, изменение - только авторизованным
- **IsOwnerOrReadOnly**: Редактирование только своих записей
- **IsLandlord**: Только владельцы жилья могут создавать объявления

---

## 💾 База данных

### Схема БД

**Основные таблицы:**

1. **users** - Пользователи
2. **listings** - Объявления
3. **listing_photos** - Фотографии
4. **blocked_dates** - Заблокированные даты
5. **bookings** - Бронирования
6. **reviews** - Отзывы
7. **search_queries** - История поиска
8. **listing_views** - Просмотры объявлений

**Связи:**
```
User (1) ----< (N) Listing
Listing (1) ----< (N) ListingPhoto
Listing (1) ----< (N) BlockedDate
Listing (1) ----< (N) Booking
Booking (1) ----< (1) Review
User (1) ----< (N) Booking (как guest)
```

---

## 🐳 Docker конфигурация

### docker-compose.yml
**Путь**: `rental_housing_api/docker-compose.yml`

**Сервисы:**

1. **db** (MySQL):
   - Image: mysql:8.0
   - Порт: 3306
   - Volume для персистентности данных

2. **web** (Django):
   - Build из Dockerfile
   - Порт: 8000
   - Зависит от db (healthcheck)
   - Gunicorn с 3 воркерами

### Dockerfile
**Путь**: `rental_housing_api/Dockerfile`

**Этапы сборки:**
1. Python 3.11-slim базовый образ
2. Установка системных зависимостей (gcc, mysql-client)
3. Установка Python пакетов
4. Копирование кода
5. Collectstatic для статики
6. Запуск Gunicorn

---

## 📊 API эндпоинты - Полный список

### Авторизация (`/api/auth/`)
- `POST /api/auth/register/` - Регистрация
- `POST /api/auth/login/` - Вход (получение токенов)
- `POST /api/auth/refresh/` - Обновление токена
- `GET /api/auth/profile/` - Профиль пользователя

### Объявления (`/api/listings/`)
- `GET /api/listings/` - Список объявлений
- `POST /api/listings/` - Создание объявления
- `GET /api/listings/{id}/` - Детали объявления
- `PUT /api/listings/{id}/` - Обновление
- `DELETE /api/listings/{id}/` - Удаление
- `GET /api/listings/my_listings/` - Мои объявления
- `POST /api/listings/{id}/upload_photo/` - Загрузка фото
- `POST /api/listings/{id}/block_dates/` - Блокировка дат

### Бронирования (`/api/bookings/`)
- `GET /api/bookings/` - Список бронирований
- `POST /api/bookings/` - Создание бронирования
- `GET /api/bookings/{id}/` - Детали бронирования
- `POST /api/bookings/{id}/confirm/` - Подтверждение
- `POST /api/bookings/{id}/cancel/` - Отмена

### Отзывы (`/api/reviews/`)
- `GET /api/reviews/` - Список отзывов
- `POST /api/reviews/` - Создание отзыва
- `GET /api/reviews/{id}/` - Детали отзыва
- `POST /api/reviews/{id}/reply/` - Ответ владельца

### Аналитика (`/api/analytics/`)
- `GET /api/analytics/popular_listings/` - Популярные объявления
- `GET /api/analytics/listing_stats/` - Статистика владельца
- `POST /api/analytics/log_search/` - Логирование поиска

---

## 🔧 Технологии

### Backend
- **Django 4.2.7** - Web фреймворк
- **Django REST Framework 3.14.0** - REST API
- **djangorestframework-simplejwt 5.3.0** - JWT авторизация
- **django-filter 23.3** - Фильтрация API
- **drf-spectacular 0.26.5** - OpenAPI документация
- **django-cors-headers 4.3.0** - CORS для фронтенда

### База данных
- **MySQL 8.0** - Основная БД
- **mysqlclient 2.2.0** - Python драйвер

### Дополнительно
- **django-money 3.4.0** - Поддержка валют
- **Pillow 10.1.0** - Обработка изображений
- **Gunicorn 21.2.0** - Production сервер

---

## 📝 Примеры использования API

### 1. Регистрация пользователя
```bash
POST /api/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "Иван Иванов",
  "password": "securepass123",
  "role": "guest"
}
```

### 2. Создание объявления
```bash
POST /api/listings/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Уютная квартира в центре",
  "description": "2-комнатная квартира со всеми удобствами",
  "city": "Киев",
  "district": "Печерск",
  "price": "1500",
  "price_currency": "UAH",
  "rooms_count": 2,
  "housing_type": "apartment",
  "max_guests": 4,
  "is_active": true
}
```

### 3. Поиск объявлений
```bash
GET /api/listings/?city=Киев&min_price=1000&max_price=2000&rooms_count=2
```

### 4. Создание бронирования
```bash
POST /api/bookings/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "listing": 1,
  "check_in": "2026-10-01",
  "check_out": "2026-10-05",
  "guests_count": 2
}
```

---

## 🎯 Ключевые особенности реализации

### 1. Мягкое удаление (Soft Delete)
- Записи не удаляются физически
- Помечаются полем `deleted_at`
- Реализовано через `SoftDeleteMixin` и `SoftDeleteManager`

### 2. Автоматический расчет цен
- В модели `Booking` метод `calculate_total_price()`
- Цена = (количество ночей) × (цена за ночь из Listing)

### 3. Валидация бронирований
- Проверка пересечений с другими бронированиями
- Проверка заблокированных дат
- Проверка максимального количества гостей

### 4. Аналитика в реальном времени
- Автоматическая запись просмотров при открытии объявления
- Подсчет популярности объявлений
- Статистика для владельцев

### 5. Мультивалютность
- Использование `django-money`
- Поддержка USD, EUR, UAH
- Хранение валюты вместе с суммой

---

## 📖 Документация API

**Swagger UI**: http://localhost:8000/api/docs/
**ReDoc**: http://localhost:8000/api/redoc/
**OpenAPI Schema**: http://localhost:8000/api/schema/

---

## 🚀 Запуск проекта

```bash
# Клонирование репозитория
cd C:\project\rental_housing_api

# Запуск через Docker
docker-compose up -d

# Создание суперпользователя (если нужно)
docker-compose exec web python manage.py createsuperuser

# Просмотр логов
docker-compose logs -f web
```

---

## ✅ Чек-лист реализованных функций

- [x] Регистрация и авторизация пользователей (JWT)
- [x] Управление объявлениями (CRUD)
- [x] Загрузка фотографий
- [x] Блокировка дат для объявлений
- [x] Система бронирований с валидацией
- [x] Автоматический расчет стоимости
- [x] Система отзывов и рейтингов
- [x] Ответы владельцев на отзывы
- [x] Поиск и фильтрация объявлений
- [x] Аналитика просмотров
- [x] Статистика для владельцев
- [x] Логирование поисковых запросов
- [x] Мягкое удаление записей
- [x] Права доступа и разграничение ролей
- [x] API документация (Swagger)
- [x] Админ-панель Django
- [x] Docker контейнеризация
- [x] MySQL база данных

---

**Дата создания документации**: 23.09.2026
**Версия проекта**: 1.0.0
**Автор**: Студент (ваше имя)
