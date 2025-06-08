from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect

class LoginRequiredMiddleware:
    """
    Middleware для принудительной авторизации на всех страницах
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Список URL, которые доступны без авторизации
        exempt_urls = [
            reverse('dashboard:login'),
            '/admin/',  # Django admin
        ]
        
        # Проверяем, если пользователь не авторизован
        if not request.user.is_authenticated:
            # Если запрос не к странице логина или админки
            if not any(request.path.startswith(url) for url in exempt_urls):
                # Редиректим на страницу логина с параметром next
                login_url = reverse('dashboard:login')
                return HttpResponseRedirect(f'{login_url}?next={request.path}')
        
        response = self.get_response(request)
        return response 