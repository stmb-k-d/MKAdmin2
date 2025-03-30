from django.db import models

class MenuItem(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    url = models.CharField(max_length=200, verbose_name='URL')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Иконка')
    order = models.IntegerField(default=0, verbose_name='Порядок')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Пункт меню'
        verbose_name_plural = 'Пункты меню'
        ordering = ['order']

    def __str__(self):
        return self.name 