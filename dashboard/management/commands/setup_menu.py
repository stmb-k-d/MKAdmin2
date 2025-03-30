from django.core.management.base import BaseCommand
from dashboard.models import MenuItem

class Command(BaseCommand):
    help = 'Добавляет предустановленные пункты меню'

    def handle(self, *args, **options):
        # Очищаем существующие пункты меню
        MenuItem.objects.all().delete()
        
        # Создаем предустановленные пункты меню
        menu_items = [
            {'name': 'Proxy', 'url': '/proxy/', 'icon': 'fas fa-globe', 'order': 1},
            {'name': 'Accs', 'url': '/accs/', 'icon': 'fas fa-user', 'order': 2},
            {'name': 'RK', 'url': '/rk/', 'icon': 'fas fa-ad', 'order': 3},
            {'name': 'Statistic', 'url': '/statistic/', 'icon': 'fas fa-chart-bar', 'order': 4},
            {'name': 'Analytics', 'url': '/analytics/', 'icon': 'fas fa-chart-line', 'order': 5},
            {'name': 'Tasks', 'url': '/tasks/', 'icon': 'fas fa-tasks', 'order': 6},
            {'name': 'Finance', 'url': '/finance/', 'icon': 'fas fa-money-bill', 'order': 7},
            {'name': 'Services', 'url': '/services/', 'icon': 'fas fa-cogs', 'order': 8},
        ]
        
        # Добавляем пункты меню
        for item in menu_items:
            MenuItem.objects.create(**item)
        
        self.stdout.write(self.style.SUCCESS('Пункты меню успешно добавлены')) 