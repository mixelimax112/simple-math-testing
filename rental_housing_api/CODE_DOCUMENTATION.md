# 📖 Подробная документация с примерами кода
# Rental Housing API - Для защиты проекта

---

## 📋 СОДЕРЖАНИЕ

1. [Models - Модели данных](#models)
2. [Serializers - Сериализаторы](#serializers)
3. [Views - Представления](#views)
4. [URLs - Маршрутизация](#urls)
5. [Permissions - Права доступа](#permissions)
6. [Settings - Настройки](#settings)

---

## 1. MODELS - Модели данных {#models}

### 1.1 User Model (users/models.py)

**ЧТО РАССКАЗАТЬ:**
> "Я создал кастомную модель пользователя, которая использует email вместо username для входа. Реализовал два типа пользователей: арендаторы (tenant) и арендодатели (landlord) через поле role."

```python
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid

class UserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User.
    Переопределяет методы создания пользователя.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Хеширование пароля
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя.
    
    Особенности:
    - Email используется как логин (вместо username)
    - Два типа пользователей: tenant и landlord
    - Поддержка soft delete через is_active
    - UUID вместо обычного ID для безопасности
    """
    
    ROLE_CHOICES = [
        ('tenant', 'Арендатор'),
        ('landlord', 'Арендодатель'),
    ]

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Уникальный идентификатор пользователя"
    )
    email = models.EmailField(
        unique=True,
        help_text="Email используется для входа в систему"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES,
        help_text="Роль определяет доступные операции"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Для soft delete - вместо физического удаления"
    )
    is_staff = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'  # Логин по email
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    @property
    def is_landlord(self):
        """Удобная проверка роли арендодателя"""
        return self.role == 'landlord'

    @property
    def is_tenant(self):
        """Удобная проверка роли арендатора"""
        return self.role == 'tenant'

    def __str__(self):
        return f"{self.email} ({self.role})"

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
```

**КЛЮЧЕВЫЕ МОМЕНТЫ ДЛЯ РАССКАЗА:**
1. `UUID` вместо обычного ID - для безопасности (сложнее подобрать)
2. `AbstractBaseUser` - полная кастомизация модели пользователя
3. `USERNAME_FIELD = 'email'` - вход по email
4. `set_password()` автоматически хеширует пароль
5. `is_active=False` для soft delete - данные остаются в БД

---

### 1.2 Listing Model (listings/models.py)

**ЧТО РАССКАЗАТЬ:**
> "Модель объявления использует django-money для работы с валютами. Реализована связь с владельцем через ForeignKey с защитой от удаления (PROTECT). Средний рейтинг рассчитывается автоматически из отзывов."

```python
from django.db import models
from djmoney.models.fields import MoneyField
from simple_history.models import HistoricalRecords
import uuid

class Listing(models.Model):
    """
    Модель объявления о сдаче жилья.
    
    Особенности:
    - MoneyField для хранения цены с валютой
    - Средний рейтинг обновляется при создании отзывов
    - HistoricalRecords сохраняет историю изменений
    - PROTECT защищает от удаления owner
    """
    
    HOUSING_TYPE_CHOICES = [
        ('apartment', 'Квартира'),
        ('house', 'Дом'),
        ('studio', 'Студия'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Связь с владельцем
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,  # Нельзя удалить user с активными объявлениями
        related_name='listings',
        help_text="Арендодатель - владелец объявления"
    )
    
    # Основная информация
    title = models.CharField(max_length=200)
    description = models.TextField()
    housing_type = models.CharField(max_length=20, choices=HOUSING_TYPE_CHOICES)
    
    # Адрес
    city = models.CharField(max_length=100, db_index=True)  # Индекс для быстрого поиска
    address = models.TextField()
    
    # Цена с валютой
    price_per_night = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='USD',
        help_text="Цена за одну ночь с указанием валюты"
    )
    
    # Характеристики
    max_guests = models.PositiveIntegerField(help_text="Максимум гостей")
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    
    # Рейтинг
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        help_text="Средняя оценка из отзывов (обновляется автоматически)"
    )
    
    # Статус
    is_active = models.BooleanField(default=True)
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # История изменений
    history = HistoricalRecords()

    def update_average_rating(self):
        """
        Автоматический пересчёт среднего рейтинга.
        Вызывается после создания/удаления отзыва.
        """
        from reviews.models import Review
        reviews = Review.objects.filter(booking__listing=self)
        if reviews.exists():
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.average_rating = round(avg, 2)
        else:
            self.average_rating = 0
        self.save()

    def __str__(self):
        return f"{self.title} - {self.city}"

    class Meta:
        db_table = 'listings'
        ordering = ['-created_at']  # Новые объявления первыми
        indexes = [
            models.Index(fields=['city', 'housing_type']),  # Составной индекс
        ]
```

**СВЯЗАННЫЕ МОДЕЛИ:**

```python
class ListingPhoto(models.Model):
    """
    Фотографии объявления.
    Поддерживает множественные фото с указанием порядка.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,  # Удаляются вместе с объявлением
        related_name='photos'
    )
    photo = models.ImageField(upload_to='listings/%Y/%m/')
    order = models.PositiveIntegerField(
        default=0,
        help_text="Порядок отображения (0 = главное фото)"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']  # Сортировка по порядку


class BlockedDate(models.Model):
    """
    Даты, когда объявление недоступно для бронирования.
    Например, личное использование владельцем.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='blocked_dates'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.listing.title}: {self.start_date} - {self.end_date}"
```

**КЛЮЧЕВЫЕ МОМЕНТЫ:**
1. `MoneyField` - автоматическая работа с валютами (USD, EUR, UAH)
2. `on_delete=models.PROTECT` - защита от случайного удаления owner
3. `HistoricalRecords()` - автоматическое сохранение истории изменений
4. `db_index=True` - ускоряет поиск по городу
5. `related_name='listings'` - удобный доступ: `user.listings.all()`

---

### 1.3 Booking Model (bookings/models.py)

**ЧТО РАССКАЗАТЬ:**
> "Модель бронирования содержит сложную валидацию: проверка пересечения дат, расчёт итоговой стоимости, ограничение максимальной длительности. На уровне базы данных добавлены constraints для предотвращения конфликтов."

```python
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q, F, CheckConstraint, ExcludeConstraint
from djmoney.models.fields import MoneyField
import uuid
from datetime import timedelta

class Booking(models.Model):
    """
    Модель бронирования.
    
    Валидация:
    - Проверка доступности дат
    - Максимум 30 ночей
    - Гости <= max_guests объявления
    - Check-out > Check-in
    - Нет пересечений с другими бронями (DB constraint)
    """
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
        ('rejected', 'Отклонено'),
        ('expired', 'Истекло'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Связи
    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.PROTECT,
        related_name='bookings'
    )
    tenant = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='bookings'
    )
    
    # Даты
    check_in = models.DateField(help_text="Дата заезда")
    check_out = models.DateField(help_text="Дата выезда")
    
    # Гости и цена
    guests_count = models.PositiveIntegerField()
    total_price = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='USD',
        help_text="Автоматически рассчитывается при создании"
    )
    
    # Статус
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Валидация на уровне модели.
        Вызывается перед save() при использовании full_clean().
        """
        errors = {}
        
        # 1. Проверка что check_out > check_in
        if self.check_out <= self.check_in:
            errors['check_out'] = "Дата выезда должна быть позже даты заезда"
        
        # 2. Проверка максимальной длительности (30 ночей)
        if (self.check_out - self.check_in).days > 30:
            errors['check_out'] = "Максимальная длительность бронирования - 30 ночей"
        
        # 3. Проверка количества гостей
        if self.guests_count > self.listing.max_guests:
            errors['guests_count'] = f"Максимум гостей: {self.listing.max_guests}"
        
        # 4. Проверка пересечения с существующими бронированиями
        overlapping = Booking.objects.filter(
            listing=self.listing,
            is_active=True,
            status__in=['pending', 'confirmed']
        ).filter(
            Q(check_in__lt=self.check_out) & Q(check_out__gt=self.check_in)
        ).exclude(pk=self.pk)  # Исключаем текущее бронирование при обновлении
        
        if overlapping.exists():
            errors['check_in'] = "Эти даты уже забронированы"
        
        # 5. Проверка блокированных дат
        from listings.models import BlockedDate
        blocked = BlockedDate.objects.filter(
            listing=self.listing,
            start_date__lt=self.check_out,
            end_date__gt=self.check_in
        )
        
        if blocked.exists():
            errors['check_in'] = "Эти даты заблокированы владельцем"
        
        if errors:
            raise ValidationError(errors)

    def calculate_total_price(self):
        """
        Автоматический расчёт итоговой стоимости.
        Стоимость = цена за ночь × количество ночей
        """
        nights = (self.check_out - self.check_in).days
        self.total_price = self.listing.price_per_night * nights

    def save(self, *args, **kwargs):
        """
        Переопределённый save для автоматического расчёта цены.
        """
        self.full_clean()  # Вызываем валидацию
        self.calculate_total_price()  # Рассчитываем цену
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.listing.title} - {self.tenant.email} ({self.status})"

    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
        
        # Constraints на уровне БД для целостности данных
        constraints = [
            # Check-out должен быть позже check-in
            CheckConstraint(
                check=Q(check_out__gt=F('check_in')),
                name='check_out_after_check_in'
            ),
            # Максимум 30 дней (проверка в днях)
            CheckConstraint(
                check=Q(check_out__lte=F('check_in') + timedelta(days=30)),
                name='max_30_nights'
            ),
        ]
```

**КЛЮЧЕВЫЕ МОМЕНТЫ:**
1. `clean()` - валидация перед сохранением в БД
2. `calculate_total_price()` - автоматический расчёт
3. `CheckConstraint` - гарантия целостности на уровне БД
4. `Q()` объекты для сложных запросов (пересечение дат)
5. `exclude(pk=self.pk)` - исключаем текущую запись при обновлении

---

### 1.4 Review Model (reviews/models.py)

**ЧТО РАССКАЗАТЬ:**
> "Отзыв связан с бронированием через OneToOne - это гарантирует, что на каждое бронирование можно оставить только один отзыв. После создания отзыва автоматически обновляется средний рейтинг объявления."

```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class Review(models.Model):
    """
    Модель отзыва на объявление.
    
    Правила:
    - Один отзыв на бронирование (OneToOne)
    - Только для completed бронирований
    - Рейтинг от 1 до 5
    - После создания обновляется average_rating объявления
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # OneToOne связь - один отзыв на бронирование
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='review',
        help_text="Отзыв привязан к конкретному бронированию"
    )
    
    # Рейтинг с валидацией 1-5
    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, "Минимальный рейтинг - 1"),
            MaxValueValidator(5, "Максимальный рейтинг - 5")
        ],
        help_text="Оценка от 1 до 5 звёзд"
    )
    
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        После сохранения отзыва обновляем средний рейтинг объявления.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Обновляем средний рейтинг объявления
        self.booking.listing.update_average_rating()

    def delete(self, *args, **kwargs):
        """
        При удалении отзыва тоже обновляем рейтинг.
        """
        listing = self.booking.listing
        super().delete(*args, **kwargs)
        listing.update_average_rating()

    def __str__(self):
        return f"Отзыв на {self.booking.listing.title} - {self.rating}★"

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
```

**КЛЮЧЕВЫЕ МОМЕНТЫ:**
1. `OneToOneField` - уникальная связь (один отзыв = одно бронирование)
2. `validators` - проверка диапазона (1-5)
3. Переопределённый `save()` и `delete()` для обновления рейтинга
4. `related_name='review'` - доступ: `booking.review`

---

## 2. SERIALIZERS - Сериализаторы {#serializers}

### 2.1 User Serializer (users/serializers.py)

**ЧТО РАССКАЗАТЬ:**
> "Сериализатор пользователя скрывает пароль при чтении и хеширует его при создании. Для регистрации используется отдельный сериализатор с валидацией пароля."

```python
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор пользователя.
    
    Особенности:
    - Пароль write_only (не отдаётся в ответах API)
    - is_landlord - read_only computed field
    """
    
    is_landlord = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'phone', 'role', 'is_landlord', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации.
    
    Особенности:
    - Подтверждение пароля
    - Автоматическое хеширование через set_password
    """
    
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Минимум 8 символов"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'role'
        ]

    def validate(self, attrs):
        """
        Проверка совпадения паролей.
        Вызывается автоматически перед save().
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Пароли не совпадают"
            })
        attrs.pop('password_confirm')  # Удаляем, не нужно сохранять
        return attrs

    def create(self, validated_data):
        """
        Создание пользователя с хешированным паролем.
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],  # Будет захеширован в create_user
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', ''),
            role=validated_data['role']
        )
        return user
```

**КЛЮЧЕВЫЕ МОМЕНТЫ:**
1. `write_only=True` - поле не возвращается в ответах API
2. `read_only=True` - поле вычисляется, не принимается в запросах
3. `validate()` - кастомная валидация перед сохранением
4. `create()` - переопределён для правильного хеширования пароля

---

### 2.2 Listing Serializer (listings/serializers.py)

**ЧТО РАССКАЗАТЬ:**
> "Сериализатор объявления автоматически связывает owner с текущим пользователем. Использует вложенные сериализаторы для фотографий. MoneyField автоматически сериализует цену с валютой."

```python
from rest_framework import serializers
from .models import Listing, ListingPhoto, BlockedDate

class ListingPhotoSerializer(serializers.ModelSerializer):
    """Вложенный сериализатор для фотографий"""
    
    class Meta:
        model = ListingPhoto
        fields = ['id', 'photo', 'order', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class ListingSerializer(serializers.ModelSerializer):
    """
    Полный сериализатор объявления.
    
    Особенности:
    - Вложенные фотографии (read-only)
    - Owner автоматически берётся из request
    - MoneyField сериализуется как {"amount": 1500, "currency": "UAH"}
    """
    
    # Вложенные фотографии (только для чтения)
    photos = ListingPhotoSerializer(many=True, read_only=True)
    
    # Информация о владельце
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    owner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'owner', 'owner_email', 'owner_name',
            'title', 'description', 'housing_type',
            'city', 'address',
            'price_per_night', 'price_per_night_currency',
            'max_guests', 'bedrooms', 'bathrooms',
            'average_rating', 'photos',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'owner', 'average_rating', 'created_at', 'updated_at'
        ]

    def get_owner_name(self, obj):
        """SerializerMethodField для вычисляемого поля"""
        return f"{obj.owner.first_name} {obj.owner.last_name}"

    def create(self, validated_data):
        """
        Автоматически устанавливаем owner из request.
        """
        request = self.context.get('request')
        validated_data['owner'] = request.user
        return super().create(validated_data)


class ListingPhotoUploadSerializer(serializers.ModelSerializer):
    """
    Отдельный сериализатор для загрузки фото.
    """
    
    class Meta:
        model = ListingPhoto
        fields = ['photo', 'order']

    def create(self, validated_data):
        listing = self.context['listing']
        return ListingPhoto.objects.create(
            listing=listing,
            **validated_data
        )
```

**КЛЮЧЕВЫЕ МОМЕНТЫ:**
1. Вложенные сериализаторы: `ListingPhotoSerializer(many=True)`
2. `source='owner.email'` - доступ к связанной модели
3. `SerializerMethodField` - для вычисляемых полей
4. `self.context['request']` - доступ к текущему запросу
5. MoneyField автоматически сериализуется в JSON

---

### 2.3 Booking Serializer (bookings/serializers.py)

**ЧТО РАССКАЗАТЬ:**
> "Сериализатор бронирования вызывает валидацию модели и автоматически привязывает tenant. Поля только для чтения показывают детали объявления без дублирования данных."

```python
from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    """
    Сериализатор бронирования.
    
    Особенности:
    - Вызывает model.full_clean() для валидации
    - Tenant автоматически из request
    - Детали объявления через вложенный сериализатор
    """
    
    # Детали объявления (read-only)
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    listing_city = serializers.CharField(source='listing.city', read_only=True)
    listing_price = serializers.DecimalField(
        source='listing.price_per_night.amount',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    # Информация о арендаторе
    tenant_email = serializers.EmailField(source='tenant.email', read_only=True)
    
    # Вычисляемое поле - количество ночей
    nights_count = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_title', 'listing_city', 'listing_price',
            'tenant', 'tenant_email',
            'check_in', 'check_out', 'nights_count',
            'guests_count', 'total_price', 'total_price_currency',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'tenant', 'total_price', 'total_price_currency',
            'status', 'created_at', 'updated_at'
        ]

    def get_nights_count(self, obj):
        """Вычисление количества ночей"""
        return (obj.check_out - obj.check_in).days

    def validate(self, attrs):
        """
        Дополнительная валидация в сериализаторе.
        """
        # Проверяем что пользователь - tenant
        request = self.context.get('request')
        if request and not request.user.is_tenant:
            raise serializers.ValidationError(
                "Только арендаторы могут создавать бронирования"
            )
        
        return attrs

    def create(self, validated_data):
        """
        Создание бронирования с автоматической привязкой tenant.
        Model.save() вызовет валидацию и расчёт цены.
        """
        request = self.context.get('request')
        validated_data['tenant'] = request.user
        
        # Создаём бронирование (будет вызван model.save())
        booking = Booking(**validated_data)
        booking.save()  # Здесь произойдёт валидация и расчёт цены
        
        return booking


class BookingStatusUpdateSerializer(serializers.Serializer):
    """
    Отдельный сериализатор для обновления статуса.
    """
    status = serializers.ChoiceField(choices=Booking.STATUS_CHOICES)

    def validate_status(self, value):
        """
        Проверка допустимых переходов статусов.
        """
        booking = self.context['booking']
        user = self.context['request'].user
        
        # Landlord может: pending → confirmed/rejected
        if user == booking.listing.owner:
            if booking.status == 'pending' and value in ['confirmed', 'rejected']:
                return value
        
        # Tenant может: pending/confirmed → cancelled
        if user == booking.tenant:
            if booking.status in ['pending', 'confirmed'] and value == 'cancelled':
                return value
        
        raise serializers.ValidationError(
            f"Недопустимый переход статуса: {booking.status} → {value}"
        )
        
        return value
```

**КЛЮЧЕВЫЕ МОМЕНТЫ:**
1. `source='listing.title'` - доступ к полю через связь
2. `SerializerMethodField` - для вычислений
3. Валидация прав доступа в `validate()`
4. Отдельный сериализатор для частичного обновления
5. Model.save() автоматически вызывает валидацию

---

## 3. VIEWS - Представления {#views}

### 3.1 Authentication Views (users/views.py)

**ЧТО РАССКАЗАТЬ:**
> "Используются ViewSets Django REST Framework для автоматической генерации CRUD операций. Добавил кастомные actions для получения профиля и обновления данных."

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.
    
    Автоматически создаёт endpoints:
    - GET /users/ - список
    - POST /users/ - создание
    - GET /users/{id}/ - детали
    - PUT/PATCH /users/{id}/ - обновление
    - DELETE /users/{id}/ - удаление
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Регистрация доступна всем, остальное - только авторизованным.
        """
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        """
        Для регистрации используем UserRegistrationSerializer.
        """
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Кастомный endpoint: GET /users/me/
        Возвращает профиль текущего пользователя.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """
        Кастомный endpoint: PUT/PATCH /users/update_profile/
        Обновление профиля текущего пользователя.
        """
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True  # PATCH - частичное обновление
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def delete_account(self, request):
        """
        Кастомный endpoint: DELETE /users/delete_account/
        Soft delete - устанавливаем is_active=False.
        """
        user = request.user
        user.is_active = False
        user.save()
        return Response(
            {"detail": "Аккаунт успешно удалён"},
            status=status.HTTP_204_NO_CONTENT
        )
```

**КЛЮЧЕВЫЕ МОМЕНТЫ:**
1. `viewsets.ModelViewSet` - автоматический CRUD
2. `@action(detail=False)` - кастомный endpoint на уровне списка
3. `detail=True` - endpoint на уровне объекта (`/users/{id}/action/`)
4. `get_permissions()` - динамические права доступа
5. `get_serializer_class()` - разные сериализаторы для разных действий

---

### 3.2 Listing Views (listings/views.py)

**ЧТО РАССКАЗАТЬ:**
> "Для объявлений реализована фильтрация через django-filter и полнотекстовый поиск. Добавил кастомные actions для загрузки фото и блокировки дат."

```python
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Listing, ListingPhoto, BlockedDate
from .serializers import (
    ListingSerializer,
    ListingPhotoUploadSerializer
)
from core.permissions import IsOwnerOrReadOnly, IsLandlord

class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet для объявлений.
    
    Фильтрация:
    - ?city=Kiev
    - ?housing_type=apartment
    - ?min_price=1000&max_price=2000
    - ?min_guests=2
    - ?search=центр
    """
    queryset = Listing.objects.filter(is_active=True).select_related('owner')
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    # Фильтрация и поиск
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['city', 'housing_type', 'max_guests']
    search_fields = ['title', 'description', 'city']
    ordering_fields = ['price_per_night', 'average_rating', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Кастомная фильтрация по цене.
        """
        queryset = super().get_queryset()
        
        # Фильтр по минимальной цене
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        
        # Фильтр по максимальной цене
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)
        
        return queryset

    def retrieve(self, request, *args, **kwargs):
        """
        Переопределённый retrieve для логирования просмотров.
        """
        instance = self.get_object()
        
        # Логируем просмотр
        from analytics.models import ViewLog
        ViewLog.objects.create(
            listing=instance,
            user=request.user if request.user.is_authenticated else None
        )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_listings(self, request):
        """
        GET /listings/my_listings/
        Мои объявления (только для landlord).
        """
        if not request.user.is_landlord:
            return Response(
                {"detail": "Доступно только арендодателям"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.filter_queryset(
            self.get_queryset().filter(owner=request.user)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def upload_photo(self, request, pk=None):
        """
        POST /listings/{id}/upload_photo/
        Загрузка фотографии объявления.
        """
        listing = self.get_object()
        
        # Проверка прав (только owner)
        if listing.owner != request.user:
            return Response(
                {"detail": "Только владелец может загружать фото"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ListingPhotoUploadSerializer(
            data=request.data,
            context={'listing': listing}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def block_dates(self, request, pk=None):
        """
        POST /listings/{id}/block_dates/
        Блокировка дат для личного использования.
        
        Body: {
            "start_date": "2026-10-01",
            "end_date": "2026-10-05",
            "reason": "Личные нужды"
        }
        """
        listing = self.get_object()
        
        if listing.owner != request.user:
            return Response(
                {"detail": "Только владелец может блокировать даты"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        blocked_date = BlockedDate.objects.create(
            listing=listing,
            start_date=request.data['start_date'],
            end_date=request.data['end_date'],
            reason=request.data.get('reason', '')
        )
        
        return Response({
            "id": str(blocked_date.id),
            "start_date": blocked_date.start_date,
            "end_date": blocked_date.end_date,
            "reason": blocked_date.reason
        }, status=status.HTTP_201_CREATED)
```

**КЛЮЧЕВЫЕ МОМЕНТЫ:**
1. `select_related('owner')` - оптимизация запросов (JOIN)
2. `DjangoFilterBackend` - автоматическая фильтрация
3. `SearchFilter` - полнотекстовый поиск
4. `get_queryset()` - кастомная фильтрация
5. Переопределённый `retrieve()` для логирования

---

## 4. URLS - Маршрутизация {#urls}

**ЧТО РАССКАЗАТЬ:**
> "Использую DefaultRouter Django REST Framework для автоматической генерации URLs. JWT токены через djangorestframework-simplejwt."

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),
    
    # API
    path('api/', include([
        # Аутентификация
        path('auth/', include('users.urls')),
        
        # Приложения
        path('listings/', include('listings.urls')),
        path('bookings/', include('bookings.urls')),
        path('reviews/', include('reviews.urls')),
        path('analytics/', include('analytics.urls')),
    ])),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from .views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # JWT токены
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User endpoints
    path('', include(router.urls)),
]

# Router автоматически создаёт:
# GET    /api/auth/users/           - список пользователей
# POST   /api/auth/users/           - регистрация
# GET    /api/auth/users/{id}/      - детали пользователя
# PUT    /api/auth/users/{id}/      - обновление
# PATCH  /api/auth/users/{id}/      - частичное обновление
# DELETE /api/auth/users/{id}/      - удаление
# GET    /api/auth/users/me/        - текущий пользователь (@action)
# PUT    /api/auth/users/update_profile/ - обновление профиля (@action)
# DELETE /api/auth/users/delete_account/ - удаление аккаунта (@action)
```

---

## 5. PERMISSIONS - Права доступа {#permissions}

**ЧТО РАССКАЗАТЬ:**
> "Создал кастомные permissions для проверки владельца объекта и роли пользователя. Это обеспечивает безопасность на уровне объектов."

```python
# core/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение на уровне объекта.
    
    - Чтение (GET) - всем
    - Изменение (PUT/PATCH/DELETE) - только владельцу
    """

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено всем
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Изменение - только владельцу
        return obj.owner == request.user


class IsLandlord(permissions.BasePermission):
    """
    Доступ только для пользователей с ролью landlord.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_landlord
        )


class IsTenant(permissions.BasePermission):
    """
    Доступ только для пользователей с ролью tenant.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_tenant
        )


class IsBookingParticipant(permissions.BasePermission):
    """
    Доступ к бронированию только для landlord или tenant.
    """

    def has_object_permission(self, request, view, obj):
        return (
            obj.tenant == request.user or
            obj.listing.owner == request.user
        )
```

---

## 6. SETTINGS - Настройки проекта {#settings}

**ЧТО РАССКАЗАТЬ:**
> "Конфигурация через переменные окружения django-environ. Поддержка MySQL и SQLite. JWT настроен с коротким временем жизни для безопасности."

```python
# config/settings.py
import os
from pathlib import Path
from datetime import timedelta
import environ

# Инициализация environ
env = environ.Env(
    DEBUG=(bool, False),
    USE_MYSQL=(bool, True),
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Чтение .env файла
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Безопасность
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-this')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Приложения
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'corsheaders',
    'drf_spectacular',
    'simple_history',
    'djmoney',

    # Apps
    'core',
    'users',
    'listings',
    'bookings',
    'reviews',
    'analytics',
]

# База данных
if env('USE_MYSQL'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env('DB_NAME', default='rental_housing'),
            'USER': env('DB_USER', default='root'),
            'PASSWORD': env('DB_PASSWORD', default=''),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Кастомная модель пользователя
AUTH_USER_MODEL = 'users.User'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT настройки
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  # Короткое время жизни
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,  # Ротация токенов
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# Swagger/OpenAPI
SPECTACULAR_SETTINGS = {
    'TITLE': 'Rental Housing API',
    'DESCRIPTION': 'Backend для платформы краткосрочной аренды жилья',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# CORS
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:3000',
    'http://127.0.0.1:3000',
])
CORS_ALLOW_CREDENTIALS = True

# Валюты
CURRENCIES = ('USD', 'EUR', 'UAH')
CURRENCY_CHOICES = [('USD', 'USD'), ('EUR', 'EUR'), ('UAH', 'UAH')]
```

---

## ✅ ЧЕКЛИСТ ДЛЯ РАССКАЗА

### Models:
- [ ] User - кастомная модель с email логином
- [ ] Listing - MoneyField для валют
- [ ] Booking - сложная валидация дат
- [ ] Review - OneToOne связь с Booking
- [ ] Constraints на уровне БД

### Serializers:
- [ ] Вложенные сериализаторы (photos)
- [ ] SerializerMethodField для вычислений
- [ ] validate() для кастомной валидации
- [ ] create() для автоматической привязки owner/tenant

### Views:
- [ ] ViewSets для автоматического CRUD
- [ ] @action для кастомных endpoints
- [ ] Фильтрация через django-filter
- [ ] Поиск через SearchFilter
- [ ] select_related для оптимизации

### Permissions:
- [ ] IsOwnerOrReadOnly
- [ ] IsLandlord / IsTenant
- [ ] IsBookingParticipant

### Settings:
- [ ] django-environ для конфигурации
- [ ] JWT с коротким lifetime
- [ ] Swagger/OpenAPI документация

---

**🎉 ГОТОВО К ЗАЩИТЕ!**
