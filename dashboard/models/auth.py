from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import secrets

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    # Переопределяем related_name для групп и разрешений чтобы избежать конфликтов
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='dashboard_user_set',
        related_query_name='dashboard_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='dashboard_user_set',
        related_query_name='dashboard_user',
    )
    
    # Основные поля - точно по структуре таблицы в PostgreSQL
    username = models.CharField(max_length=150, blank=True, null=True)
    password = models.CharField(max_length=128)  # Django поле для пароля
    password_hash = models.CharField(max_length=255, blank=True, null=True)  # Ваше поле
    email = models.CharField(max_length=254, unique=True)
    
    # Для сессий и безопасности
    session_token = models.CharField(max_length=255, blank=True, null=True)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    password_reset_token = models.CharField(max_length=255, blank=True, null=True)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    
    # Временные метки
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    last_login_at = models.DateTimeField(blank=True, null=True)
    password_changed_at = models.DateTimeField(blank=True, null=True)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    
    # IP и защита от брутфорса
    registration_ip = models.CharField(max_length=45, blank=True, null=True)
    last_login_ip = models.CharField(max_length=45, blank=True, null=True)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)
    
    # Статусы
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    # Дополнительно
    timezone = models.CharField(max_length=50, blank=True, null=True)
    language = models.CharField(max_length=10, blank=True, null=True)
    
    # Двухфакторная аутентификация
    two_factor_secret = models.CharField(max_length=255, blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        managed = False  # Django не будет управлять этой таблицей

    @property
    def is_staff(self):
        return self.is_admin
    
    @property  
    def is_superuser(self):
        return self.is_admin
    
    @property
    def last_login(self):
        return self.last_login_at
        
    @last_login.setter
    def last_login(self, value):
        self.last_login_at = value

    def generate_session_token(self):
        self.session_token = secrets.token_urlsafe(32)
        self.save(update_fields=['session_token'])

    def clear_session_token(self):
        self.session_token = None
        self.save(update_fields=['session_token'])

    def is_account_locked(self):
        if self.locked_until:
            return timezone.now() < self.locked_until
        return False

    def increment_failed_attempts(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_attempts', 'locked_until'])

    def __str__(self):
        return self.email 