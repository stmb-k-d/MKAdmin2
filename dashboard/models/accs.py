from django.db import models

class FacebookAccount(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('inactive', 'Неактивен'),
        ('blocked', 'Заблокирован'),
        ('pending', 'На проверке'),
    ]

    account_id = models.CharField(max_length=100, unique=True, verbose_name='ID аккаунта')
    name = models.CharField(max_length=255, verbose_name='Название')
    email = models.EmailField(verbose_name='Email')
    password = models.CharField(max_length=255, verbose_name='Пароль')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Баланс')
    currency = models.CharField(max_length=3, default='USD', verbose_name='Валюта')
    last_check = models.DateTimeField(auto_now=True, verbose_name='Последняя проверка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Аккаунт Facebook'
        verbose_name_plural = 'Аккаунты Facebook'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"

class AccountProxy(models.Model):
    account = models.ForeignKey(FacebookAccount, on_delete=models.CASCADE, related_name='proxies', verbose_name='Аккаунт')
    proxy = models.ForeignKey('dashboard.Proxy', on_delete=models.CASCADE, related_name='accounts', verbose_name='Прокси')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Прокси аккаунта'
        verbose_name_plural = 'Прокси аккаунтов'
        unique_together = ['account', 'proxy']

    def __str__(self):
        return f"{self.account.name} - {self.proxy}" 