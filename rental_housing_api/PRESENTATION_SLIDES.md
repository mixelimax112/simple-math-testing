# 🎓 Презентация проекта: Rental Housing API

## Слайд 1: Титульный слайд
```
═══════════════════════════════════════════════════════
        RENTAL HOUSING API
    Backend для платформы аренды жилья
═══════════════════════════════════════════════════════

           Автор: Maksym
           Дата: Сентябрь 2026
           
    Django REST Framework | JWT | Docker | MySQL
═══════════════════════════════════════════════════════
```

---

## Слайд 2: Что такое Rental Housing API?

### 🏠 Описание проекта
**Backend для платформы краткосрочной аренды жилья (аналог Airbnb)**

### 🎯 Цель
Создать полнофункциональный REST API для:
- Публикации объявлений о жилье
- Поиска и бронирования недвижимости
- Системы отзывов и рейтингов
- Аналитики и статистики

### 👥 Целевая аудитория
- **Арендодатели** - размещают объявления
- **Арендаторы** - ищут и бронируют жильё

---

## Слайд 3: Технологический стек

### 🛠 Backend
- **Django 4.2** - веб-фреймворк
- **Django REST Framework 3.14** - REST API
- **Python 3.11**

### 🔐 Аутентификация
- **JWT токены** (djangorestframework-simplejwt)
- Access token: 1 час
- Refresh token: 7 дней

### 💾 База данных
- **MySQL 8.0** (production)
- **SQLite** (development)

### 🚀 Деплой
- **Docker** + **Docker Compose**
- **Gunicorn** (WSGI server)
- **Nginx** (reverse proxy)

### 📚 Документация
- **drf-spectacular** (Swagger/OpenAPI)

---

## Слайд 4: Архитектура системы

```
┌─────────────────────────────────────────────────┐
│                   CLIENT                        │
│        (Browser, Mobile App, Postman)           │
└──────────────────┬──────────────────────────────┘
                   │ HTTP/HTTPS
                   ▼
┌─────────────────────────────────────────────────┐
│                  NGINX                          │
│         (Reverse Proxy, Static Files)           │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│                GUNICORN                         │
│              (WSGI Server)                      │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│             DJANGO REST API                     │
│  ┌─────────────────────────────────────────┐   │
│  │ Users │ Listings │ Bookings │ Reviews   │   │
│  └─────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│              MySQL DATABASE                     │
│         (Users, Listings, Bookings...)          │
└─────────────────────────────────────────────────┘
```

---

## Слайд 5: Функциональные возможности

### 1️⃣ Управление пользователями
✅ Регистрация с выбором роли (landlord/tenant)  
✅ JWT аутентификация  
✅ Обновление профиля  
✅ Soft delete аккаунтов  

### 2️⃣ Объявления (Listings)
✅ CRUD операции  
✅ Загрузка фотографий  
✅ Фильтрация (город, цена, тип, гости)  
✅ Полнотекстовый поиск  
✅ Блокировка дат  

### 3️⃣ Бронирования (Bookings)
✅ Создание с валидацией дат  
✅ Автоматический расчёт стоимости  
✅ Управление статусами  
✅ Защита от пересечений  

### 4️⃣ Отзывы (Reviews)
✅ Рейтинг от 1 до 5  
✅ Только для завершённых бронирований  
✅ Автообновление среднего рейтинга  

### 5️⃣ Аналитика
✅ Популярные объявления  
✅ Статистика просмотров  
✅ Часто используемые запросы  

---

## Слайд 6: Модели данных

### 👤 User (Пользователь)
```
- email (логин)
- password (хешированный)
- first_name, last_name
- role: tenant | landlord
- phone
```

### 🏠 Listing (Объявление)
```
- owner (FK → User)
- title, description
- housing_type: apartment | house | studio
- city, address
- price_per_night (с валютой)
- max_guests, bedrooms, bathrooms
- average_rating (автоматически)
```

### 📅 Booking (Бронирование)
```
- listing (FK → Listing)
- tenant (FK → User)
- check_in, check_out
- guests_count
- total_price (автоматически)
- status: pending | confirmed | completed | cancelled
```

### ⭐ Review (Отзыв)
```
- booking (OneToOne → Booking)
- rating (1-5)
- comment
```

---

## Слайд 7: API Endpoints (25+)

### 🔐 Аутентификация (`/api/auth/`)
- `POST /register/` - Регистрация
- `POST /login/` - Получение JWT
- `POST /token/refresh/` - Обновление токена
- `GET /users/me/` - Текущий пользователь

### 🏠 Объявления (`/api/listings/`)
- `GET /` - Список с фильтрами
- `POST /` - Создать (landlord only)
- `GET /{id}/` - Детали
- `PUT/DELETE /{id}/` - Обновить/Удалить
- `POST /{id}/upload_photo/` - Загрузить фото
- `POST /{id}/block_dates/` - Заблокировать даты
- `GET /my_listings/` - Мои объявления

### 📅 Бронирования (`/api/bookings/`)
- `GET /` - Список
- `POST /` - Создать (tenant only)
- `POST /{id}/update_status/` - Изменить статус
- `GET /my_bookings/` - Мои бронирования
- `GET /landlord_bookings/` - Брони моих объявлений

### ⭐ Отзывы (`/api/reviews/`)
- `GET /` - Список
- `POST /` - Создать
- `GET /{id}/` - Детали
- `GET /my_reviews/` - Мои отзывы

### 📊 Аналитика (`/api/analytics/`)
- `GET /popular_listings/` - Топ объявлений
- `GET /popular_searches/` - Популярные запросы
- `GET /listing_stats/` - Статистика объявления

---

## Слайд 8: Безопасность

### 🔒 Аутентификация
✅ JWT токены с коротким lifetime  
✅ Ротация refresh токенов  
✅ Хеширование паролей (PBKDF2)  

### 🛡 Авторизация
✅ Permissions на уровне объектов  
✅ IsOwner, IsLandlord, IsTenant  
✅ Role-based access control  

### ✔️ Валидация
✅ Проверка пересечения дат бронирований  
✅ Ограничение длительности (макс. 30 ночей)  
✅ Constraints на уровне БД  
✅ Email validation  

### 🚫 Защита от атак
✅ Django ORM → SQL injection protection  
✅ CSRF protection  
✅ CORS настройки  
✅ Soft delete → предотвращение потери данных  

---

## Слайд 9: Swagger UI - Живая демонстрация

### 📚 Интерактивная документация
```
http://localhost:8000/api/docs/
```

**Возможности:**
- 🔍 Просмотр всех endpoints
- ▶️ Тестирование API в браузере
- 📝 Автоматическая генерация из кода
- 🔐 Авторизация через JWT
- 📋 Примеры запросов/ответов

### Альтернативы:
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

---

## Слайд 10: Пример работы API

### Сценарий: Создание бронирования

```
1. POST /api/auth/register/
   → Регистрация арендатора
   → Получение user_id

2. POST /api/auth/login/
   → email + password
   → Получение access_token

3. GET /api/listings/?city=Kiev&min_price=1000
   → Поиск объявлений
   → Получение списка

4. POST /api/bookings/
   Headers: Authorization: Bearer <token>
   Body: {
     "listing": "uuid",
     "check_in": "2026-10-01",
     "check_out": "2026-10-05",
     "guests_count": 2
   }
   → Валидация дат ✓
   → Расчёт стоимости ✓
   → Создание брони со статусом "pending"

5. GET /api/bookings/my_bookings/
   → Просмотр моих бронирований
```

---

## Слайд 11: Особенности реализации

### 🎨 Архитектурные решения

**1. Soft Delete вместо физического удаления**
```python
class SoftDeleteModel(models.Model):
    is_active = models.BooleanField(default=True)
    
    def delete(self):
        self.is_active = False
        self.save()
```
*Сохраняет историю и защищает от потери данных*

**2. Автоматический расчёт стоимости**
```python
def calculate_total_price(self):
    nights = (self.check_out - self.check_in).days
    self.total_price = self.listing.price_per_night * nights
```

**3. Защита от пересечений на уровне БД**
```python
class Meta:
    constraints = [
        CheckConstraint(
            check=Q(check_out__gt=F('check_in')),
            name='check_out_after_check_in'
        ),
        ExcludeConstraint(...)  # Пересечение дат
    ]
```

**4. История изменений**
```python
# django-simple-history
from simple_history.models import HistoricalRecords

class Listing(models.Model):
    history = HistoricalRecords()
```

---

## Слайд 12: Docker и деплой

### 🐳 Контейнеризация

**docker-compose.yml:**
```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: rental_housing_db
  
  web:
    build: .
    command: gunicorn config.wsgi:application
    depends_on:
      - db
    ports:
      - "8000:8000"
```

### 🚀 Запуск одной командой
```bash
docker-compose up -d --build
```

### ☁️ Готов к деплою на:
- AWS EC2
- DigitalOcean
- Heroku
- Railway
- Render

---

## Слайд 13: Метрики проекта

### 📊 Статистика

| Метрика | Значение |
|---------|----------|
| Строк кода | 3000+ |
| Моделей данных | 8 |
| API Endpoints | 25+ |
| Приложений Django | 6 |
| Зависимостей | 15 |
| Время разработки | 2 недели |

### ✅ Покрытие функционала
- [x] CRUD для всех сущностей
- [x] Аутентификация и авторизация
- [x] Валидация бизнес-логики
- [x] Документация API
- [x] Docker конфигурация
- [x] Готовность к production

---

## Слайд 14: Что можно добавить в будущем

### 🚀 Roadmap развития

**1. Платежи**
- Интеграция Stripe/PayPal
- Эскроу платежи
- Автоматические выплаты landlord

**2. Уведомления**
- Email через Celery + Redis
- SMS уведомления
- Push notifications

**3. Коммуникации**
- WebSocket чат
- Видеозвонки для показа жилья

**4. Геолокация**
- Интеграция Google Maps
- Поиск по радиусу
- Построение маршрутов

**5. Machine Learning**
- Рекомендации объявлений
- Динамическое ценообразование
- Детекция мошенничества

**6. Mobile App**
- React Native приложение
- Push уведомления
- Офлайн режим

---

## Слайд 15: Выводы

### ✨ Достижения проекта

✅ **Полнофункциональный REST API** с 25+ endpoints  
✅ **Современный технологический стек** (Django, JWT, Docker)  
✅ **Безопасность** на всех уровнях  
✅ **Валидация бизнес-логики** на уровне кода и БД  
✅ **Автоматическая документация** (Swagger/OpenAPI)  
✅ **Готовность к деплою** через Docker  
✅ **Масштабируемая архитектура**  

### 🎓 Полученные навыки
- Backend разработка на Django
- Проектирование REST API
- Работа с JWT аутентификацией
- Docker и контейнеризация
- Валидация и безопасность
- Документирование API

### 💼 Применение
Проект демонстрирует знание современных практик backend-разработки и готов к использованию в реальных условиях.

---

## Слайд 16: Демонстрация

### 🎬 LIVE DEMO

**Откроем в браузере:**

1. **Swagger UI**: http://localhost:8000/api/docs/
   - Покажем список endpoints
   - Зарегистрируем пользователя
   - Получим JWT токен
   - Создадим объявление
   - Создадим бронирование

2. **Admin Panel**: http://localhost:8000/admin/
   - Покажем управление данными
   - Историю изменений

### ❓ Вопросы?

---

## Слайд 17: Контакты и ссылки

### 📫 Информация о проекте

**Репозиторий:** C:\project\rental_housing_api

**Документация:**
- `TECHNICAL_DOCUMENTATION.md` - полная техническая документация
- `PRESENTATION_GUIDE.md` - руководство по защите
- `README.md` - описание и инструкция по запуску
- `DEPLOYMENT.md` - инструкция по деплою на AWS

**Технологии:**
- Django 4.2
- Django REST Framework 3.14
- JWT Authentication
- MySQL 8.0
- Docker + Docker Compose
- Swagger/OpenAPI

---

### 🎉 СПАСИБО ЗА ВНИМАНИЕ!

**Проект готов к демонстрации и использованию в production!**

═══════════════════════════════════════════════════════
         Rental Housing API by Maksym
              Сентябрь 2026
═══════════════════════════════════════════════════════
