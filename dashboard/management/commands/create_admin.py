from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import secrets

class Command(BaseCommand):
    help = 'Создать пользователя admin@mk.com с паролем 8872'

    def handle(self, *args, **options):
        email = 'admin@mk.com'
        password = '8872'
        
        try:
            with connection.cursor() as cursor:
                # Проверяем, существует ли уже пользователь
                cursor.execute("SELECT email FROM users WHERE email = %s", [email])
                if cursor.fetchone():
                    self.stdout.write(
                        self.style.WARNING(f'Пользователь {email} уже существует')
                    )
                    return
                
                # Создаем пользователя
                hashed_password = make_password(password)
                current_time = timezone.now()
                
                cursor.execute("""
                    INSERT INTO users (
                        email, password, username, is_active, is_admin, 
                        created_at, updated_at, failed_login_attempts,
                        timezone, language
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    email,
                    hashed_password,
                    'admin',
                    True,  # is_active
                    True,  # is_admin
                    current_time,
                    current_time,
                    0,  # failed_login_attempts
                    'UTC',
                    'ru'
                ])
                
                self.stdout.write(
                    self.style.SUCCESS(f'Успешно создан пользователь {email} с паролем {password}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка создания пользователя: {str(e)}')
            ) 