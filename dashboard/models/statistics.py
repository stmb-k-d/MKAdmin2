from django.db import models
from .rk import Campaign, AdSet, Ad

class CampaignStatistic(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='statistics', verbose_name='Кампания')
    date = models.DateField(verbose_name='Дата')
    impressions = models.IntegerField(default=0, verbose_name='Показы')
    clicks = models.IntegerField(default=0, verbose_name='Клики')
    ctr = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='CTR')
    spend = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Потрачено')
    conversions = models.IntegerField(default=0, verbose_name='Конверсии')
    cost_per_conversion = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Стоимость конверсии')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Статистика кампании'
        verbose_name_plural = 'Статистика кампаний'
        unique_together = ['campaign', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.campaign.name} - {self.date}"

class AdSetStatistic(models.Model):
    ad_set = models.ForeignKey(AdSet, on_delete=models.CASCADE, related_name='statistics', verbose_name='Группа объявлений')
    date = models.DateField(verbose_name='Дата')
    impressions = models.IntegerField(default=0, verbose_name='Показы')
    clicks = models.IntegerField(default=0, verbose_name='Клики')
    ctr = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='CTR')
    spend = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Потрачено')
    conversions = models.IntegerField(default=0, verbose_name='Конверсии')
    cost_per_conversion = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Стоимость конверсии')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Статистика группы объявлений'
        verbose_name_plural = 'Статистика групп объявлений'
        unique_together = ['ad_set', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.ad_set.name} - {self.date}"

class AdStatistic(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='statistics', verbose_name='Объявление')
    date = models.DateField(verbose_name='Дата')
    impressions = models.IntegerField(default=0, verbose_name='Показы')
    clicks = models.IntegerField(default=0, verbose_name='Клики')
    ctr = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='CTR')
    spend = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Потрачено')
    conversions = models.IntegerField(default=0, verbose_name='Конверсии')
    cost_per_conversion = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Стоимость конверсии')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Статистика объявления'
        verbose_name_plural = 'Статистика объявлений'
        unique_together = ['ad', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.ad.name} - {self.date}" 