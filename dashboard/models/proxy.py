from django.db import models

class Proxy(models.Model):
    PROXY_TYPES = [
        ('http', 'HTTP'),
        ('socks4', 'SOCKS4'),
        ('socks5', 'SOCKS5'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('inactive', 'Неактивен'),
        ('blocked', 'Заблокирован'),
    ]

    ip = models.GenericIPAddressField(verbose_name='IP адрес')
    port = models.IntegerField(verbose_name='Порт')
    proxy_type = models.CharField(max_length=10, choices=PROXY_TYPES, verbose_name='Тип прокси')
    username = models.CharField(max_length=100, blank=True, null=True, verbose_name='Логин')
    password = models.CharField(max_length=100, blank=True, null=True, verbose_name='Пароль')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    last_check = models.DateTimeField(auto_now=True, verbose_name='Последняя проверка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Прокси'
        verbose_name_plural = 'Прокси'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.proxy_type}://{self.ip}:{self.port}"

    def get_proxy_url(self):
        if self.username and self.password:
            return f"{self.proxy_type}://{self.username}:{self.password}@{self.ip}:{self.port}"
        return f"{self.proxy_type}://{self.ip}:{self.port}" 