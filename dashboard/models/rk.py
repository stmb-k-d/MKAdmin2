from django.db import models
from .accs import FacebookAccount

class Campaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('active', 'Активна'),
        ('paused', 'Приостановлена'),
        ('completed', 'Завершена'),
        ('archived', 'В архиве'),
    ]

    BUDGET_TYPES = [
        ('daily', 'Ежедневный'),
        ('lifetime', 'Общий'),
    ]

    account = models.ForeignKey(FacebookAccount, on_delete=models.CASCADE, related_name='campaigns', verbose_name='Аккаунт')
    campaign_id = models.CharField(max_length=100, unique=True, verbose_name='ID кампании')
    name = models.CharField(max_length=255, verbose_name='Название')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    budget_type = models.CharField(max_length=10, choices=BUDGET_TYPES, default='daily', verbose_name='Тип бюджета')
    daily_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Ежедневный бюджет')
    total_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Общий бюджет')
    spent = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Потрачено')
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата начала')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Рекламная кампания'
        verbose_name_plural = 'Рекламные кампании'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.account.name})"

class AdSet(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('active', 'Активен'),
        ('paused', 'Приостановлен'),
        ('completed', 'Завершен'),
        ('archived', 'В архиве'),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='ad_sets', verbose_name='Кампания')
    ad_set_id = models.CharField(max_length=100, unique=True, verbose_name='ID группы объявлений')
    name = models.CharField(max_length=255, verbose_name='Название')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    daily_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Ежедневный бюджет')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Группа объявлений'
        verbose_name_plural = 'Группы объявлений'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.campaign.name})"

class Ad(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('active', 'Активно'),
        ('paused', 'Приостановлено'),
        ('completed', 'Завершено'),
        ('archived', 'В архиве'),
    ]

    ad_set = models.ForeignKey(AdSet, on_delete=models.CASCADE, related_name='ads', verbose_name='Группа объявлений')
    ad_id = models.CharField(max_length=100, unique=True, verbose_name='ID объявления')
    name = models.CharField(max_length=255, verbose_name='Название')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.ad_set.name})" 