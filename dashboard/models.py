from django.db import models

# Create your models here.

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class Proxy(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('inactive', 'Неактивный'),
        ('checking', 'Проверка'),
        ('unknown', 'Неизвестно'),
    ]

    proxy_id = models.AutoField(primary_key=True)
    ip = models.GenericIPAddressField()
    type = models.CharField(max_length=50)
    login = models.CharField(max_length=100, null=True, blank=True)
    psw = models.CharField(max_length=100, null=True, blank=True)
    port_socks5 = models.IntegerField()
    port_https = models.IntegerField()
    geo = models.CharField(max_length=50)
    link_change_ip = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    proxy_cost = models.DecimalField(max_digits=10, decimal_places=2)
    proxy_cur = models.CharField(max_length=10)
    accs = models.CharField(max_length=100, null=True, blank=True)
    fbt_id = models.CharField(max_length=100, null=True, blank=True)
    for_octo = models.BooleanField(default=False)
    octo_uuid = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.ip}:{self.port_socks5}"

# Создаем предустановленные пункты меню
DEFAULT_MENU_ITEMS = [
    {'name': 'Proxy', 'url': '/proxy/', 'icon': 'fas fa-globe'},
    {'name': 'Accs', 'url': '/accs/', 'icon': 'fas fa-user'},
    {'name': 'RK', 'url': '/rk/', 'icon': 'fas fa-ad'},
    {'name': 'Statistic', 'url': '/statistic/', 'icon': 'fas fa-chart-bar'},
    {'name': 'Analytics', 'url': '/analytics/', 'icon': 'fas fa-chart-line'},
    {'name': 'Tasks', 'url': '/tasks/', 'icon': 'fas fa-tasks'},
    {'name': 'Finance', 'url': '/finance/', 'icon': 'fas fa-money-bill'},
    {'name': 'Services', 'url': '/services/', 'icon': 'fas fa-cogs'},
]
