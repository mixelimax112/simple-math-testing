from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from simple_history.models import HistoricalRecords

from core.models import TimestampedMixin, SoftDeleteMixin, SoftDeleteManager


class UserManager(BaseUserManager, SoftDeleteManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'landlord')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimestampedMixin, SoftDeleteMixin):
    ROLE_CHOICES = [
        ('tenant', 'Арендатор'),
        ('landlord', 'Арендодатель'),
    ]

    email = models.EmailField(unique=True, verbose_name='Email')
    name = models.CharField(max_length=255, verbose_name='Имя')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='tenant', verbose_name='Роль')
    is_landlord = models.BooleanField(default=False, verbose_name='Арендодатель')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')

    objects = UserManager()
    history = HistoricalRecords()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'users'

    def __str__(self):
        return f"{self.name} ({self.email})"

    def save(self, *args, **kwargs):
        self.is_landlord = (self.role == 'landlord')
        super().save(*args, **kwargs)
