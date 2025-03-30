from django.core.management.base import BaseCommand
from dashboard.models import Proxy

class Command(BaseCommand):
    help = 'Добавляет тестовые прокси'

    def handle(self, *args, **options):
        # Очищаем существующие прокси
        Proxy.objects.all().delete()
        
        # Создаем тестовые прокси
        test_proxies = [
            {
                'ip': '192.168.1.1',
                'port': 8080,
                'proxy_type': 'http',
                'username': 'user1',
                'password': 'pass1',
                'status': 'active'
            },
            {
                'ip': '192.168.1.2',
                'port': 8081,
                'proxy_type': 'socks5',
                'username': 'user2',
                'password': 'pass2',
                'status': 'inactive'
            },
            {
                'ip': '192.168.1.3',
                'port': 8082,
                'proxy_type': 'socks4',
                'username': None,
                'password': None,
                'status': 'blocked'
            }
        ]
        
        # Добавляем прокси
        for proxy_data in test_proxies:
            Proxy.objects.create(**proxy_data)
        
        self.stdout.write(self.style.SUCCESS('Тестовые прокси успешно добавлены')) 