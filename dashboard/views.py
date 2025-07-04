from django.shortcuts import render, redirect
from django.db import connection
from .models import MenuItem, Campaign, AdSet, Ad, Proxy, User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
import sys
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.contrib import messages
import logging
from django.db import transaction
from zoneinfo import ZoneInfo
from .forms import LoginForm
from django.utils import timezone

logger = logging.getLogger(__name__)

def get_client_ip(request):
    """Получить IP-адрес клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def login_view(request):
    """Вход в систему"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Обновляем данные последнего входа
            user.last_login_at = timezone.now()
            user.last_login_ip = get_client_ip(request)
            user.generate_session_token()
            
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.email}!')
            
            # Редирект на следующую страницу или главную
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Ошибка входа в систему')
    else:
        form = LoginForm()
    
    return render(request, 'dashboard/login.html', {
        'form': form,
        'title': 'Вход в систему'
    })

def logout_view(request):
    """Выход из системы"""
    if request.user.is_authenticated:
        # Очищаем session token
        try:
            user = User.objects.get(id=request.user.id)
            user.clear_session_token()
        except User.DoesNotExist:
            pass
        
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы')
    
    return redirect('dashboard:login')

def get_menu_items():
    return [
        {'name': 'dashboard', 'title': 'Дашборд', 'icon': 'fas fa-tachometer-alt'},
        {'name': 'proxy', 'title': 'Прокси', 'icon': 'fas fa-server'},
        {
            'name': 'facebook', 
            'title': 'Facebook', 
            'icon': 'fab fa-facebook',
            'submenu': [
                {'name': 'accs', 'title': 'Accounts', 'icon': 'fas fa-users'},
                {'name': 'rk', 'title': 'Ads Cabinets', 'icon': 'fas fa-chart-line'},
                {'name': 'campaigns', 'title': 'Campaigns', 'icon': 'fas fa-bullhorn'},
                {'name': 'adsets', 'title': 'Adsets', 'icon': 'fas fa-layer-group'},
                {'name': 'ads', 'title': 'Ads', 'icon': 'fas fa-ad'},
            ]
        },
        {'name': 'statistic', 'title': 'Статистика', 'icon': 'fas fa-chart-bar'},
        {'name': 'analytics', 'title': 'Аналитика', 'icon': 'fas fa-chart-pie',
         'direct_link': True,
         'submenu': [
             {'name': 'kpi', 'title': 'KPI', 'icon': 'fas fa-tachometer-alt'},
             {'name': 'offers', 'title': 'Офферы', 'icon': 'fas fa-tags'},
             {'name': 'bundles', 'title': 'Связки', 'icon': 'fas fa-link'},
         ]
        },
        {'name': 'tasks', 'title': 'Задачи', 'icon': 'fas fa-tasks'},
        {'name': 'finance', 'title': 'Финансы', 'icon': 'fas fa-money-bill-wave'},
        {'name': 'services', 'title': 'Сервисы', 'icon': 'fas fa-cogs'},
        {'name': 'balance', 'title': 'Баланс:0.00', 'icon': '', 'no_link': True},
        {'name': 'notifications', 'title': '', 'icon': 'fas fa-bell'},
        {'name': 'profile', 'title': 'Профиль', 'icon': 'fas fa-user-circle',
         'submenu': [
             {'name': 'working_log', 'title': 'Working Log', 'icon': 'fas fa-clipboard-list'},
             {'name': 'extra', 'title': 'Экстра', 'icon': 'fas fa-star'},
             {'name': 'team', 'title': 'Команда', 'icon': 'fas fa-users'},
         ]
        },
        {'name': 'logout', 'title': 'Выход', 'icon': 'fas fa-sign-out-alt', 'special': 'logout'},
    ]

@login_required
def index(request):
    return render(request, 'dashboard/index.html', {
        'menu_items': get_menu_items(),
        'title': 'Главная',
        'page_title': 'Панель управления'
    })

@login_required
def proxy(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM proxy_data')
        columns = [col[0] for col in cursor.description]
        proxies = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    context = {
        'menu_items': get_menu_items(),
        'title': 'Прокси',
        'page_title': 'Управление прокси',
        'proxies': proxies,
    }
    return render(request, 'dashboard/proxy.html', context)

@login_required
def check_proxy(request, proxy_id):
    try:
        proxy = Proxy.objects.get(id=proxy_id)
        # Здесь будет логика проверки прокси
        return JsonResponse({'success': True})
    except Proxy.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Прокси не найден'})

@login_required
def delete_proxy(request, proxy_id):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Проверяем существование прокси
                cursor.execute("SELECT proxy_id FROM proxy_data WHERE proxy_id = %s", [proxy_id])
                if cursor.fetchone():
                    # Удаляем прокси
                    cursor.execute("DELETE FROM proxy_data WHERE proxy_id = %s", [proxy_id])
                    return JsonResponse({'success': True, 'message': 'Прокси успешно удален'})
                else:
                    return JsonResponse({'success': False, 'error': 'Прокси не найден'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Ошибка при удалении: {str(e)}'})
    else:
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})

@login_required
def count_free_proxies(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM proxy_data WHERE accs IS NULL')
        count = cursor.fetchone()[0]
    return JsonResponse({'count': count})

@login_required
def accs_view(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM accs_data')
        columns = [col[0] for col in cursor.description]
        accounts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Получаем список всех колонок для выбора пользователем
        all_columns = columns
    
    # Сериализуем данные аккаунтов в JSON для передачи в шаблон
    accounts_json = json.dumps(accounts, default=str)
    
    return render(request, 'dashboard/accs.html', {
        'menu_items': get_menu_items(),
        'title': 'Аккаунты',
        'page_title': 'Управление аккаунтами',
        'accounts_json': accounts_json,
        'all_columns': json.dumps(all_columns)
    })

@login_required
def accs_detail(request, account_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM accs_data WHERE id_acc_bd = %s", [account_id])
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        if row:
            account = dict(zip(columns, row))
            # Обрабатываем rk_list если оно существует
            if account.get('rk_list'):
                try:
                    # Если rk_list - это строка JSON, парсим её
                    if isinstance(account['rk_list'], str):
                        account['rk_list'] = json.loads(account['rk_list'])
                    # Если это уже список, оставляем как есть
                    elif not isinstance(account['rk_list'], list):
                        account['rk_list'] = None
                except (json.JSONDecodeError, TypeError):
                    account['rk_list'] = None
        else:
            account = None

    context = {
        'menu_items': get_menu_items(),
        'title': 'Детали аккаунта',
        'page_title': 'Детали аккаунта',
        'account': account,
    }
    return render(request, 'dashboard/accs_detail.html', context)

@login_required
def rk_view(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id,
                id_acc_bd,
                geo_buying,
                app_id,
                creo_id,
                type_optimization,
                fb_effective_status,
                fb_status,
                fb_clicks,
                fb_cost_per_unique_click,
                fb_cpc,
                fb_cpm,
                fb_ctr,
                fb_impressions,
                fb_objective,
                fb_spend,
                fb_quality_score_organic,
                fb_quality_score_ectr,
                fb_quality_score_ecvr,
                fb_link_click,
                fb_video_view,
                fb_page_engagement,
                fb_post_engagement,
                fb_post_reaction,
                last_update_fbt,
                rk_id,
                time_zone,
                kt_campaign_name,
                kt_unic_clicks,
                c2i,
                cr2i,
                cpi,
                regs,
                cr2r,
                i2r,
                cpr,
                cr2d,
                r2s,
                cps,
                deps,
                income,
                bprofit,
                broi,
                last_update_fbt,
                install_or_dep,
                last_update_kt,
                kt_campaign_id,
                comment,
                fp,
                live_status,
                rk_limit,
                spend_warm,
                rk_geo_warm,
                rk_geo_buying,
                cards,
                rk_cur,
                ad_id,
                pixel_id,
                vertical,
                pixel_token
            FROM rk_data
        """)
        columns = [col[0] for col in cursor.description]
        rks = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return render(request, 'dashboard/rk.html', {
        'menu_items': get_menu_items(),
        'title': 'РК',
        'page_title': 'Рекламные кабинеты',
        'rks': rks
    })

@login_required
def statistic_view(request):
    return render(request, 'dashboard/statistic.html', {
        'menu_items': get_menu_items(),
        'title': 'Статистика',
        'page_title': 'Статистика'
    })

@login_required
def analytics_view(request):
    return render(request, 'dashboard/analytics.html', {
        'menu_items': get_menu_items(),
        'title': 'Аналитика',
        'page_title': 'Аналитика'
    })

@login_required
def tasks_view(request):
    return render(request, 'dashboard/tasks.html', {
        'menu_items': get_menu_items(),
        'title': 'Задачи',
        'page_title': 'Управление задачами'
    })

@login_required
def finance_view(request):
    return render(request, 'dashboard/finance.html', {
        'menu_items': get_menu_items(),
        'title': 'Финансы',
        'page_title': 'Финансы'
    })

@login_required
def services_view(request):
    return render(request, 'dashboard/services.html', {
        'menu_items': get_menu_items(),
        'title': 'Сервисы',
        'page_title': 'Управление сервисами'
    })

@login_required
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html', {
        'menu_items': get_menu_items(),
        'title': 'Дашборд',
        'page_title': 'Главная страница'
    })

@login_required
def proxy_detail(request, proxy_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM proxy_data WHERE proxy_id = %s", [proxy_id])
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        if row:
            proxy = dict(zip(columns, row))
        else:
            proxy = None

    context = {
        'menu_items': get_menu_items(),
        'title': 'Детали прокси',
        'page_title': 'Детали прокси',
        'proxy': proxy,
    }
    return render(request, 'dashboard/proxy_detail.html', context)

@login_required
def rk_detail(request, rk_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM rk_data WHERE id = %s
        """, [rk_id])
        columns = [col[0] for col in cursor.description]
        rk = dict(zip(columns, cursor.fetchone()))
    
    context = {
        'menu_items': get_menu_items(),
        'rk': rk
    }
    return render(request, 'dashboard/rk_detail.html', context)

@login_required
def campaigns(request):
    return render(request, 'dashboard/campaigns.html', {
        'menu_items': get_menu_items()
    })

@login_required
def adsets(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM adset_data')
        columns = [col[0] for col in cursor.description]
        adsets = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Получаем список всех колонок для выбора пользователем
        all_columns = columns
    
    return render(request, 'dashboard/adsets.html', {
        'menu_items': get_menu_items(),
        'title': 'Adsets',
        'page_title': 'Наборы объявлений',
        'adsets': adsets,
        'all_columns': json.dumps(all_columns)
    })

@login_required
def ads(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM ad_data')
        columns = [col[0] for col in cursor.description]
        ads = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Получаем список всех колонок для выбора пользователем
        all_columns = columns
    
    return render(request, 'dashboard/ads.html', {
        'menu_items': get_menu_items(),
        'title': 'Ads',
        'page_title': 'Креативы',
        'ads': ads,
        'all_columns': json.dumps(all_columns)
    })

@login_required
def ad_detail(request, ad_id):
    # Получаем HTTP_REFERER и определяем URL для возврата
    http_referer = request.META.get('HTTP_REFERER', '')
    
    # Определяем, откуда пришел пользователь, и формируем соответствующий URL
    if '/statistic/facebook/' in http_referer:
        back_url = http_referer
        back_text = 'Назад к статистике'
    elif '/ads/' in http_referer:
        back_url = http_referer
        back_text = 'Назад к списку объявлений'
    else:
        # Если referer неизвестен или отсутствует, используем ссылку на ads
        back_url = reverse('dashboard:ads')
        back_text = 'Назад к списку объявлений'
    
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM ad_data WHERE ad_id = %s', [ad_id])
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
        if not results:
            # Если объявление не найдено, редиректим на список объявлений
            return redirect('ads')
        
        ad = dict(zip(columns, results[0]))
        
        # Получаем статистику по дням для этого объявления
        cursor.execute('''
            SELECT 
                date_log, fb_spend, fb_cpm, fb_impressions, fb_clicks, 
                fb_ctr, fb_cpc, fb_link_click, fb_cost_per_unique_click,
                kt_unic_clicks, c2i, cr2i, cpi, regs, cr2r, i2r, cpr,
                cr2d, r2s, cps, deps, income, bprofit, broi
            FROM ad_data_daily 
            WHERE ad_id = %s 
            ORDER BY date_log DESC
        ''', [ad_id])
        
        daily_columns = [col[0] for col in cursor.description]
        daily_stats = [dict(zip(daily_columns, row)) for row in cursor.fetchall()]
        
        # Получаем логи для этого объявления из таблицы working_log
        ad_logs = []
        try:
            # Проверяем существование таблицы working_log
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'working_log'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                # Получаем логи где в msg упоминается ad_id
                cursor.execute('''
                    SELECT datetime, msg, msg_decription, categorie, type, sub_user, notification
                    FROM working_log 
                    WHERE msg ILIKE %s 
                    ORDER BY datetime DESC 
                    LIMIT 100
                ''', [f'%{ad_id}%'])
                
                log_columns = [col[0] for col in cursor.description]
                ad_logs = [dict(zip(log_columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            # Если ошибка с таблицей логов, продолжаем без логов
            logger.error(f"Ошибка при получении логов для объявления {ad_id}: {str(e)}")
    
    return render(request, 'dashboard/ad_detail.html', {
        'menu_items': get_menu_items(),
        'title': f'Ad Detail: {ad_id}',
        'page_title': f'Объявление: {ad_id}',
        'ad': ad,
        'daily_stats': daily_stats,
        'ad_logs': ad_logs,
        'back_url': back_url,
        'back_text': back_text
    })

@login_required
def update_kt_campaign_id(request, ad_id):
    logger.info(f"Вызов функции update_kt_campaign_id для ad_id={ad_id}, метод: {request.method}")
    
    if request.method == 'POST':
        new_kt_campaign_id = request.POST.get('kt_campaign_id', '').strip()
        logger.info(f"Получено новое значение kt_campaign_id: {new_kt_campaign_id}")
        
        # Проверяем, что введенное значение не пустое
        if not new_kt_campaign_id:
            messages.error(request, 'kt_campaign_id не может быть пустым')
            return redirect('dashboard:ad_detail', ad_id=ad_id)
        
        # Проверяем, что введенное значение - это целое число
        try:
            new_kt_campaign_id = int(new_kt_campaign_id)
            logger.info(f"Успешно преобразовано в int: {new_kt_campaign_id}")
            
            # Выполняем обновление в базе данных
            try:
                with connection.cursor() as cursor:
                    # Начинаем транзакцию
                    connection.set_autocommit(False)
                    
                    # Обновляем kt_campaign_id в основной таблице ad_data
                    cursor.execute(
                        'UPDATE ad_data SET kt_campaign_id = %s WHERE ad_id = %s',
                        [new_kt_campaign_id, ad_id]
                    )
                    
                    # Обновляем kt_campaign_id в таблице ежедневной статистики ad_data_daily
                    cursor.execute(
                        'UPDATE ad_data_daily SET kt_campaign_id = %s WHERE ad_id = %s',
                        [new_kt_campaign_id, ad_id]
                    )
                    
                    # Фиксируем транзакцию
                    connection.commit()
                    
                    # Логируем успешное обновление
                    logger.info(f"kt_campaign_id для объявления {ad_id} обновлен на {new_kt_campaign_id}")
                    
                    # Добавляем сообщение об успешном обновлении
                    messages.success(request, f'kt_campaign_id успешно обновлен на {new_kt_campaign_id}')
                    
                    # Восстанавливаем автокоммит
                    connection.set_autocommit(True)
                    
            except Exception as e:
                # В случае ошибки откатываем транзакцию и логируем ошибку
                connection.rollback()
                connection.set_autocommit(True)
                
                logger.error(f"Ошибка при обновлении kt_campaign_id для {ad_id}: {str(e)}")
                messages.error(request, f'Ошибка при обновлении kt_campaign_id: {str(e)}')
        except ValueError:
            messages.error(request, 'kt_campaign_id должен быть целым числом')
    
    # Перенаправляем на страницу детального просмотра объявления
    return redirect('dashboard:ad_detail', ad_id=ad_id)

@login_required
def update_id_acc_bd(request, ad_id):
    logger.info(f"Вызов функции update_id_acc_bd для ad_id={ad_id}, метод: {request.method}")
    
    if request.method == 'POST':
        new_id_acc_bd = request.POST.get('id_acc_bd', '').strip()
        logger.info(f"Получено новое значение id_acc_bd: {new_id_acc_bd}")
        
        # Проверяем, что введенное значение не пустое
        if not new_id_acc_bd:
            messages.error(request, 'id_acc_bd не может быть пустым')
            return redirect('dashboard:ad_detail', ad_id=ad_id)
        
        # Проверяем, что введенное значение - это целое число
        try:
            new_id_acc_bd = int(new_id_acc_bd)
            logger.info(f"Успешно преобразовано в int: {new_id_acc_bd}")
            
            # Выполняем обновление в базе данных
            try:
                with connection.cursor() as cursor:
                    # Начинаем транзакцию
                    connection.set_autocommit(False)
                    
                    # Проверяем существование аккаунта с указанным id_acc_bd
                    cursor.execute(
                        'SELECT id_acc_bd FROM accs_data WHERE id_acc_bd = %s',
                        [new_id_acc_bd]
                    )
                    account_exists = cursor.fetchone()
                    
                    if not account_exists:
                        connection.set_autocommit(True)
                        messages.error(request, f'Аккаунт с id_acc_bd={new_id_acc_bd} не существует')
                        return redirect('dashboard:ad_detail', ad_id=ad_id)
                    
                    # Обновляем id_acc_bd в основной таблице ad_data
                    cursor.execute(
                        'UPDATE ad_data SET id_acc_bd = %s WHERE ad_id = %s',
                        [new_id_acc_bd, ad_id]
                    )
                    
                    # Обновляем id_acc_bd в таблице ежедневной статистики ad_data_daily
                    cursor.execute(
                        'UPDATE ad_data_daily SET id_acc_bd = %s WHERE ad_id = %s',
                        [new_id_acc_bd, ad_id]
                    )
                    
                    # Фиксируем транзакцию
                    connection.commit()
                    
                    # Логируем успешное обновление
                    logger.info(f"id_acc_bd для объявления {ad_id} обновлен на {new_id_acc_bd}")
                    
                    # Добавляем сообщение об успешном обновлении
                    messages.success(request, f'id_acc_bd успешно обновлен на {new_id_acc_bd}')
                    
                    # Восстанавливаем автокоммит
                    connection.set_autocommit(True)
                    
            except Exception as e:
                # В случае ошибки откатываем транзакцию и логируем ошибку
                connection.rollback()
                connection.set_autocommit(True)
                
                logger.error(f"Ошибка при обновлении id_acc_bd для {ad_id}: {str(e)}")
                messages.error(request, f'Ошибка при обновлении id_acc_bd: {str(e)}')
        except ValueError:
            messages.error(request, 'id_acc_bd должен быть целым числом')
    
    # Перенаправляем на страницу детального просмотра объявления
    return redirect('dashboard:ad_detail', ad_id=ad_id)

def bulk_update_ads(request):
    """
    Функция для группового обновления параметров креативов
    """
    logger.info(f"Вызов функции bulk_update_ads, метод: {request.method}")
    
    if request.method == 'POST':
        parameter = request.POST.get('parameter', '').strip()
        value = request.POST.get('value', '').strip()
        ad_ids_str = request.POST.get('ad_ids', '').strip()
        
        logger.info(f"Получены параметры: parameter={parameter}, value={value}, ad_ids={ad_ids_str}")
        
        # Валидация входных данных
        if not parameter or not value or not ad_ids_str:
            messages.error(request, 'Все поля должны быть заполнены')
            return redirect('dashboard:ads')
        
        # Проверяем допустимые параметры
        allowed_parameters = ['id_acc_bd', 'kt_campaign_id']
        if parameter not in allowed_parameters:
            messages.error(request, f'Недопустимый параметр: {parameter}')
            return redirect('dashboard:ads')
        
        # Парсим список ID объявлений
        try:
            ad_ids = [ad_id.strip() for ad_id in ad_ids_str.split(',') if ad_id.strip()]
            if not ad_ids:
                messages.error(request, 'Не выбраны объявления для обновления')
                return redirect('dashboard:ads')
        except Exception as e:
            logger.error(f"Ошибка при парсинге ad_ids: {str(e)}")
            messages.error(request, 'Ошибка в формате списка объявлений')
            return redirect('dashboard:ads')
        
        # Проверяем, что значение - целое число
        try:
            new_value = int(value)
            logger.info(f"Успешно преобразовано в int: {new_value}")
        except ValueError:
            messages.error(request, f'{parameter} должен быть целым числом')
            return redirect('dashboard:ads')
        
        # Выполняем обновление в базе данных
        try:
            with connection.cursor() as cursor:
                # Начинаем транзакцию
                connection.set_autocommit(False)
                
                updated_count = 0
                
                # Дополнительная валидация для id_acc_bd
                if parameter == 'id_acc_bd':
                    # Проверяем существование аккаунта с указанным id_acc_bd
                    cursor.execute(
                        'SELECT id_acc_bd FROM accs_data WHERE id_acc_bd = %s',
                        [new_value]
                    )
                    account_exists = cursor.fetchone()
                    
                    if not account_exists:
                        connection.set_autocommit(True)
                        messages.error(request, f'Аккаунт с id_acc_bd={new_value} не существует')
                        return redirect('dashboard:ads')
                
                # Обновляем каждое объявление
                for ad_id in ad_ids:
                    # Проверяем существование объявления
                    cursor.execute(
                        'SELECT ad_id FROM ad_data WHERE ad_id = %s',
                        [ad_id]
                    )
                    ad_exists = cursor.fetchone()
                    
                    if ad_exists:
                        # Обновляем в основной таблице ad_data
                        if parameter == 'id_acc_bd':
                            cursor.execute(
                                'UPDATE ad_data SET id_acc_bd = %s WHERE ad_id = %s',
                                [new_value, ad_id]
                            )
                        elif parameter == 'kt_campaign_id':
                            cursor.execute(
                                'UPDATE ad_data SET kt_campaign_id = %s WHERE ad_id = %s',
                                [new_value, ad_id]
                            )
                        
                        # Обновляем в таблице ежедневной статистики ad_data_daily
                        if parameter == 'id_acc_bd':
                            cursor.execute(
                                'UPDATE ad_data_daily SET id_acc_bd = %s WHERE ad_id = %s',
                                [new_value, ad_id]
                            )
                        elif parameter == 'kt_campaign_id':
                            cursor.execute(
                                'UPDATE ad_data_daily SET kt_campaign_id = %s WHERE ad_id = %s',
                                [new_value, ad_id]
                            )
                        
                        updated_count += 1
                        logger.info(f"{parameter} для объявления {ad_id} обновлен на {new_value}")
                    else:
                        logger.warning(f"Объявление {ad_id} не найдено в базе данных")
                
                # Фиксируем транзакцию
                connection.commit()
                
                # Логируем успешное обновление
                logger.info(f"Групповое обновление завершено. Обновлено {updated_count} из {len(ad_ids)} объявлений")
                
                # Добавляем сообщение об успешном обновлении
                if updated_count > 0:
                    messages.success(request, f'Успешно обновлено {updated_count} объявлений. {parameter} установлен в {new_value}')
                else:
                    messages.warning(request, 'Ни одно объявление не было обновлено')
                
                # Восстанавливаем автокоммит
                connection.set_autocommit(True)
                
        except Exception as e:
            # В случае ошибки откатываем транзакцию и логируем ошибку
            connection.rollback()
            connection.set_autocommit(True)
            
            logger.error(f"Ошибка при групповом обновлении: {str(e)}")
            messages.error(request, f'Ошибка при групповом обновлении: {str(e)}')
    
    # Перенаправляем на страницу списка объявлений
    return redirect('dashboard:ads')

def working_log(request):
    try:
        # Получаем параметр поиска из запроса
        search_query = request.GET.get('search', '').strip()
        
        with connection.cursor() as cursor:
            # Проверяем существование таблицы (PostgreSQL)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'working_log'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                return render(request, 'dashboard/working_log.html', {
                    'error': 'Таблица working_log не существует в базе данных',
                    'menu_items': get_menu_items(),
                    'title': 'Working Log',
                    'page_title': 'Working Log'
                })
            
            # Получаем список колонок (PostgreSQL)
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'working_log'
                ORDER BY ordinal_position;
            """)
            columns = [row[0] for row in cursor.fetchall()]
            
            # Строим SQL запрос с учетом поиска и ЛИМИТОМ
            sql = "SELECT * FROM working_log"
            params = []
            
            if search_query:
                # Создаем условия поиска по всем текстовым полям
                search_conditions = []
                for col in columns:
                    if col in ['msg', 'msg_decription', 'categorie', 'type', 'sub_user', 'notification']:
                        search_conditions.append(f"{col}::text ILIKE %s")
                        params.append(f'%{search_query}%')
                
                if search_conditions:
                    sql += " WHERE " + " OR ".join(search_conditions)
            
            # Сортируем по datetime в убывающем порядке и ОГРАНИЧИВАЕМ
            sql += " ORDER BY datetime DESC LIMIT 1000"
            
            # Выполняем запрос
            cursor.execute(sql, params)
            
            data = []
            for row in cursor.fetchall():
                item = {}
                for i, col in enumerate(columns):
                    # Форматирование данных
                    if col == 'datetime' and row[i]:
                        # Пытаемся распарсить datetime и конвертировать в лондонскую таймзону
                        try:
                            if hasattr(row[i], 'strftime'):
                                # Если это datetime объект из БД
                                dt = row[i]
                                
                                # Определяем лондонскую таймзону
                                london_tz = ZoneInfo('Europe/London')
                                
                                # Если datetime не имеет информации о таймзоне, считаем что это UTC
                                if dt.tzinfo is None:
                                    dt = dt.replace(tzinfo=ZoneInfo('UTC'))
                                
                                # Конвертируем в лондонскую таймзону
                                london_dt = dt.astimezone(london_tz)
                                
                                # Форматируем в строку
                                item[col] = london_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
                            else:
                                # Если это строка, пытаемся распарсить
                                try:
                                    dt = datetime.fromisoformat(str(row[i]).replace('Z', '+00:00'))
                                    london_tz = ZoneInfo('Europe/London')
                                    
                                    if dt.tzinfo is None:
                                        dt = dt.replace(tzinfo=ZoneInfo('UTC'))
                                    
                                    london_dt = dt.astimezone(london_tz)
                                    item[col] = london_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
                                except:
                                    item[col] = str(row[i])
                        except Exception as e:
                            # В случае ошибки оставляем исходное значение
                            item[col] = str(row[i])
                    else:
                        item[col] = row[i]
                data.append(item)
            
            return render(request, 'dashboard/working_log.html', {
                'data': data,
                'columns': columns,
                'search_query': search_query,
                'menu_items': get_menu_items(),
                'title': 'Working Log',
                'page_title': 'Working Log'
            })
            
    except Exception as e:
        return render(request, 'dashboard/working_log.html', {
            'error': f'Ошибка при получении данных: {str(e)}',
            'menu_items': get_menu_items(),
            'title': 'Working Log',
            'page_title': 'Working Log'
        })

def extra_view(request):
    return render(request, 'dashboard/extra.html', {
        'menu_items': get_menu_items(),
        'page_title': 'Экстра'
    })

def bundles_view(request):
    return render(request, 'dashboard/bundles.html', {
        'menu_items': get_menu_items(),
        'page_title': 'Связки'
    })

def notifications_view(request):
    return render(request, 'dashboard/notifications.html', {
        'menu_items': get_menu_items(),
        'page_title': 'Уведомления'
    })

def profile_view(request):
    context = {
        'menu_items': get_menu_items(),
        'title': 'Профиль',
        'page_title': 'Управление профилем'
    }
    return render(request, 'dashboard/profile.html', context)

def team_view(request):
    context = {
        'menu_items': get_menu_items(),
        'title': 'Команда',
        'page_title': 'Управление командой'
    }
    return render(request, 'dashboard/team.html', context)

def lp_view(request):
    return render(request, 'dashboard/lp.html', {
        'menu_items': get_menu_items(),
        'title': 'LP',
        'page_title': 'LP'
    })

def deposit_stats_view(request):
    return render(request, 'dashboard/deposit_stats.html', {
        'menu_items': get_menu_items(),
        'title': 'Статистика по попыткам депозитов',
        'page_title': 'Статистика по попыткам депозитов'
    })

def time_deposit_stats_view(request):
    return render(request, 'dashboard/time_deposit_stats.html', {
        'menu_items': get_menu_items(),
        'title': 'Статистика по времени депозитов/ребиллов',
        'page_title': 'Статистика по времени депозитов/ребиллов'
    })

def facebook_stats_view(request):
    """
    Отображает данные статистики Facebook из таблицы ad_data_daily
    """
    try:
        # Получаем параметры фильтрации по датам из запроса
        # Если параметры не указаны, используем сегодняшнюю дату по умолчанию
        from datetime import date
        today = date.today().strftime('%Y-%m-%d')
        
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Устанавливаем дефолтные значения на сегодня, если параметры пустые
        if not date_from and not date_to:
            date_from = today
            date_to = today
        
        # Проверяем существование таблицы
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'ad_data_daily'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                return render(request, 'dashboard/facebook_stats.html', {
                    'error': 'Таблица ad_data_daily не существует. Создайте таблицу с помощью скрипта create_ad_data_daily.sql',
                    'menu_items': get_menu_items(),
                    'title': 'Facebook Statistics',
                    'page_title': 'Статистика Facebook'
                })
            
            # Получаем список колонок
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'ad_data_daily'
                ORDER BY ordinal_position;
            """)
            columns = [row[0] for row in cursor.fetchall()]
            
            # Строим SQL запрос с учетом фильтрации по датам
            sql = "SELECT * FROM ad_data_daily"
            params = []
            where_conditions = []
            
            if date_from:
                where_conditions.append("date_log >= %s")
                params.append(date_from)
            
            if date_to:
                where_conditions.append("date_log <= %s")
                params.append(date_to)
            
            if where_conditions:
                sql += " WHERE " + " AND ".join(where_conditions)
            
            # Забираем полный набор строк за выбранный диапазон (ограничение не нужно, иначе теряем данные)
            sql += " ORDER BY date_log DESC"
            
            # Выполняем запрос
            cursor.execute(sql, params)
            
            data = []
            for row in cursor.fetchall():
                item = {}
                for i, col in enumerate(columns):
                    # Форматирование данных
                    if col == 'date_log' and row[i]:
                        item[col] = row[i].strftime('%Y-%m-%d')
                    elif col in ['fb_ctr', 'fb_cr'] and row[i]:
                        item[col] = f"{float(row[i]):.2%}"
                    elif col in ['fb_spend', 'fb_cpm', 'fb_cpc'] and row[i]:
                        item[col] = f"{float(row[i]):.2f}"
                    else:
                        item[col] = row[i]
                data.append(item)
            
            # Получаем сохраненные отчеты пользователя
            saved_reports = []
            if request.user.is_authenticated:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT report_name, reports_structure_list, report_dates, report_filters
                            FROM users_report_data 
                            WHERE user_id = %s
                        """, [request.user.id])
                        
                        report_columns = [col[0] for col in cursor.description]
                        saved_reports = []
                        for row in cursor.fetchall():
                            report_dict = {}
                            for i, col in enumerate(report_columns):
                                report_dict[col] = row[i]
                            saved_reports.append(report_dict)
                except Exception as e:
                    logger.error(f'Ошибка при получении сохраненных отчетов: {e}')
                    saved_reports = []
            
            return render(request, 'dashboard/facebook_stats.html', {
                'data': data,
                'columns': columns,
                'menu_items': get_menu_items(),
                'title': 'Facebook Statistics',
                'page_title': 'Статистика Facebook',
                'date_from': date_from,
                'date_to': date_to,
                'saved_reports': list(saved_reports)
            })
            
    except Exception as e:
        return render(request, 'dashboard/facebook_stats.html', {
            'error': f'Ошибка при получении данных: {str(e)}',
            'menu_items': get_menu_items(),
            'title': 'Facebook Statistics',
            'page_title': 'Статистика Facebook'
        })

def get_facebook_stats_data(request):
    """
    API для получения отфильтрованных и сгруппированных данных из таблицы ad_data_daily
    """
    try:
        filters = json.loads(request.GET.get('filters', '{}'))
        group_by = request.GET.getlist('group_by', [])
        aggregation_type = request.GET.get('aggregation_type', 'sum')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Валидация параметров
        valid_aggregation_types = ['sum', 'avg', 'min', 'max', 'count']
        if aggregation_type not in valid_aggregation_types:
            return JsonResponse({'error': 'Неверный тип агрегации'})
        
        # Строим SQL запрос
        select_clause = []
        group_clause = []
        where_conditions = []
        aggregation_metrics = [
            'fb_spend', 'fb_impressions', 'fb_clicks', 'fb_cpm', 'fb_cpc', 'fb_ctr', 
            'fb_actions', 'fb_cr', 'fb_cpa'
        ]
        
        # Добавляем поля группировки
        for field in group_by:
            select_clause.append(f"{field}")
            group_clause.append(f"{field}")
        
        # Если группировка не указана, выбираем все столбцы
        if not group_by:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'ad_data_daily'
                    ORDER BY ordinal_position;
                """)
                columns = [row[0] for row in cursor.fetchall()]
                select_clause = columns
        else:
            # Добавляем агрегации
            for metric in aggregation_metrics:
                if aggregation_type == 'sum':
                    select_clause.append(f"SUM({metric}) as {metric}")
                elif aggregation_type == 'avg':
                    select_clause.append(f"AVG({metric}) as {metric}")
                elif aggregation_type == 'min':
                    select_clause.append(f"MIN({metric}) as {metric}")
                elif aggregation_type == 'max':
                    select_clause.append(f"MAX({metric}) as {metric}")
                elif aggregation_type == 'count':
                    select_clause.append(f"COUNT({metric}) as {metric}")
        
        # Фильтр по дате
        if date_from:
            where_conditions.append(f"date_log >= '{date_from}'")
        if date_to:
            where_conditions.append(f"date_log <= '{date_to}'")
        
        # Добавляем фильтры
        for column, conditions in filters.items():
            for condition in conditions:
                operator = condition['operator']
                value = condition['value']
                
                if operator == 'eq':
                    where_conditions.append(f"{column} = '{value}'")
                elif operator == 'neq':
                    where_conditions.append(f"{column} != '{value}'")
                elif operator == 'gt':
                    where_conditions.append(f"{column} > {value}")
                elif operator == 'lt':
                    where_conditions.append(f"{column} < {value}")
                elif operator == 'gte':
                    where_conditions.append(f"{column} >= {value}")
                elif operator == 'lte':
                    where_conditions.append(f"{column} <= {value}")
                elif operator == 'contains':
                    where_conditions.append(f"{column} LIKE '%{value}%'")
                elif operator == 'in':
                    values = [v.strip() for v in value.split(',')]
                    values_str = "'" + "','".join(values) + "'"
                    where_conditions.append(f"{column} IN ({values_str})")
        
        # Соединяем всё вместе в SQL запрос
        sql = f"SELECT {', '.join(select_clause)} FROM ad_data_daily"
        
        if where_conditions:
            sql += f" WHERE {' AND '.join(where_conditions)}"
        
        if group_clause:
            sql += f" GROUP BY {', '.join(group_clause)}"
        
        sql += " ORDER BY " + (f"{group_by[0]}" if group_by else "date_log") + " DESC LIMIT 5000"
        
        # Выполняем запрос
        with connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            
            data = []
            for row in cursor.fetchall():
                item = {}
                for i, col in enumerate(columns):
                    # Форматирование данных
                    if col == 'date_log' and row[i]:
                        item[col] = row[i].strftime('%Y-%m-%d')
                    elif col in ['fb_ctr', 'fb_cr'] and row[i]:
                        item[col] = f"{float(row[i]):.2%}"
                    elif col in ['fb_spend', 'fb_cpm', 'fb_cpc', 'fb_cpa'] and row[i]:
                        item[col] = f"{float(row[i]):.2f}"
                    else:
                        item[col] = row[i]
                data.append(item)
            
            return JsonResponse({
                'data': data,
                'columns': columns
            })
            
    except Exception as e:
        return JsonResponse({'error': f'Ошибка при получении данных: {str(e)}'})

def get_facebook_stats_chart_data(request):
    """
    API для получения данных для графиков статистики с поддержкой множественных метрик
    """
    try:
        # Поддержка нескольких метрик
        metrics = request.GET.getlist('metrics', ['fb_spend'])
        # Обратная совместимость с single метрикой
        if not metrics and request.GET.get('metric'):
            metrics = [request.GET.get('metric')]
            
        group_by = request.GET.get('group_by', 'date_log')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Фильтры
        where_conditions = []
        if date_from:
            where_conditions.append(f"date_log >= '{date_from}'")
        if date_to:
            where_conditions.append(f"date_log <= '{date_to}'")
        
        # Строим SQL запрос с несколькими метриками
        select_clause = [f"{group_by} as label"]
        for metric in metrics:
            select_clause.append(f"SUM({metric}) as {metric}")
        
        sql = f"""
            SELECT {', '.join(select_clause)}
            FROM ad_data_daily
        """
        
        if where_conditions:
            sql += f" WHERE {' AND '.join(where_conditions)}"
        
        sql += f" GROUP BY {group_by} ORDER BY {group_by} ASC LIMIT 50"
        
        # Выполняем запрос
        with connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            
            data = []
            for row in cursor.fetchall():
                item = {}
                for i, col in enumerate(columns):
                    # Форматирование даты
                    if col == 'label' and row[i] and hasattr(row[i], 'strftime'):
                        item[col] = row[i].strftime('%Y-%m-%d')
                    else:
                        # Конвертация чисел в float для JSON сериализации
                        item[col] = float(row[i]) if row[i] is not None else 0
                data.append(item)
            
            return JsonResponse({
                'data': data
            })
            
    except Exception as e:
        return JsonResponse({'error': f'Ошибка при получении данных для графика: {str(e)}'})

def offers_view(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM offers_rates')
        columns = [col[0] for col in cursor.description]
        offers = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return render(request, 'dashboard/offers.html', {
        'menu_items': get_menu_items(),
        'title': 'Офферы',
        'page_title': 'Управление офферами',
        'offers': offers
    })

def edit_offer(request, offer_id):
    if request.method == 'POST':
        offer_id_kt = request.POST.get('offer_id_kt')
        offer_name_kt = request.POST.get('offer_name_kt')
        geo = request.POST.get('geo')
        rate_usd = request.POST.get('rate_usd')
        
        with connection.cursor() as cursor:
            cursor.execute(
                'UPDATE offers_rates SET offer_name_kt = %s, geo = %s, rate_usd = %s WHERE offer_id_kt = %s',
                [offer_name_kt, geo, rate_usd, offer_id_kt]
            )
        
        return redirect('dashboard:offers')
    
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM offers_rates WHERE offer_id_kt = %s', [offer_id])
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        if row is None:
            return JsonResponse({'error': 'Оффер не найден'}, status=404)
        offer_data = dict(zip(columns, row))
    
    return JsonResponse(offer_data)

def kpi_view(request):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT id, kt_campaign_id, kt_campaign_name, cpi, cpr, cps, broi,
                   type_optimization, type
            FROM kpi_controller
        ''')
        columns = [col[0] for col in cursor.description]
        raw_kpi_list = cursor.fetchall()
        
        kpi_list = []
        for row in raw_kpi_list:
            item = dict(zip(columns, row))
            # Преобразуем None в пустую строку для отображения
            for key, val in item.items():
                if val is None:
                    item[key] = ""
            kpi_list.append(item)
    
    return render(request, 'dashboard/kpi.html', {
        'menu_items': get_menu_items(),
        'title': 'KPI',
        'page_title': 'KPI',
        'kpi_list': kpi_list
    })

def get_kpi_data(request, kpi_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT * FROM kpi_controller WHERE id = %s
            ''', [kpi_id])
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()
            if row:
                kpi = dict(zip(columns, row))
                return JsonResponse(kpi)
            else:
                return JsonResponse({'error': 'KPI не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def update_kpi(request, kpi_id):
    """Обновляет запись в kpi_controller по первичному ключу id."""
    if request.method != 'POST':
        logger.warning(f"[update_kpi] Вызван с методом {request.method}, ожидается POST")
        return redirect('dashboard:kpi')

    logger.info(f"[update_kpi] POST для id={kpi_id} (тип: {type(kpi_id)}): {request.POST.dict()}")

    try:
        # Убедимся, что kpi_id - это целое число
        kpi_id = int(kpi_id)
        logger.info(f"[update_kpi] ID преобразован в число: {kpi_id}")
    except (ValueError, TypeError):
        logger.error(f"[update_kpi] Ошибка преобразования ID к числу: {kpi_id}")
        messages.error(request, f'Некорректный ID: {kpi_id}')
        return redirect('dashboard:kpi')

    # Список числовых полей для явного преобразования типов
    numeric_fields = ['fb_cpc', 'fb_cpm', 'c2i', 'cr2i', 'cpi', 'cr2r', 'i2r', 
                      'cpr', 'cr2d', 'r2s', 'cps', 'broi', 'cpa_dep', 'kt_campaign_id']
                      
    editable_fields = [
        'kt_campaign_id', 'kt_campaign_name', 'fb_cpc', 'fb_cpm', 'c2i', 'cr2i',
        'cpi', 'cr2r', 'i2r', 'cpr', 'cr2d', 'r2s', 'cps', 'broi', 'cpa_dep',
        'link_camp', 'creo_id', 'type_optimization', 'type', 'send_to'
    ]

    set_clauses = []
    params = []
    for field in editable_fields:
        value = request.POST.get(field)
        # Обрабатываем пустые строки для числовых полей - устанавливаем их в NULL
        if field in numeric_fields and (value == '' or value is None):
            set_clauses.append(f"{field} = %s")
            params.append(None)  # NULL в базе данных
            logger.debug(f"[update_kpi] Установка NULL для пустого поля {field}")
        elif value is not None and value != '':
            # Преобразование числовых полей
            if field in numeric_fields:
                try:
                    # Пробуем преобразовать в число с плавающей точкой
                    if '.' in value or ',' in value:
                        value = float(value.replace(',', '.'))
                    else:
                        value = int(value)
                    logger.debug(f"[update_kpi] Преобразовано числовое поле {field}={value}")
                except (ValueError, TypeError):
                    logger.warning(f"[update_kpi] Не удалось преобразовать поле {field}='{value}' в число")
                    # Пропускаем некорректные значения
                    continue
                    
            set_clauses.append(f"{field} = %s")
            params.append(value)
            logger.debug(f"[update_kpi] Добавлено поле {field}={value} (тип: {type(value)})")

    if not set_clauses:
        logger.warning(f"[update_kpi] Нет изменений для сохранения id={kpi_id}")
        messages.warning(request, 'Нет изменений для сохранения')
        return redirect('dashboard:kpi')

    params.append(kpi_id)
    sql = f"UPDATE kpi_controller SET {', '.join(set_clauses)} WHERE id = %s"
    logger.info(f"[update_kpi] SQL: {sql}")
    logger.info(f"[update_kpi] Параметры: {params}")

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                logger.info(f"[update_kpi] Выполняется запрос для id={kpi_id}")
                # Сначала проверим существование записи
                cursor.execute("SELECT EXISTS(SELECT 1 FROM kpi_controller WHERE id = %s)", [kpi_id])
                exists = cursor.fetchone()[0]
                if not exists:
                    logger.warning(f"[update_kpi] Запись с id={kpi_id} не найдена")
                    messages.warning(request, f'Запись KPI #{kpi_id} не найдена в базе данных')
                    return redirect('dashboard:kpi')
                
                # Теперь выполняем обновление
                cursor.execute(sql, params)
                affected = cursor.rowcount
                logger.info(f"[update_kpi] Запрос выполнен, rowcount={affected}")
                
                if affected == 0:
                    logger.info(f"[update_kpi] Запись с id={kpi_id} существует, но не обновлена")
                    messages.warning(request, f'Данные для KPI #{kpi_id} не изменились или совпадают (ROWCOUNT=0)')
                else:
                    logger.info(f"[update_kpi] Запись успешно обновлена, id={kpi_id}")
                    messages.success(request, f'KPI #{kpi_id} успешно обновлён (ROWCOUNT={affected})')
    except Exception as exc:
        logger.exception(f'[update_kpi] Ошибка при обновлении id={kpi_id}: %s', exc)
        messages.error(request, f'Ошибка при обновлении: {exc}')

    return redirect('dashboard:kpi')

@csrf_exempt
def update_proxy_id(request):
    """Обновляет proxy_id для аккаунта в таблице accs_data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        # Парсим JSON данные из тела запроса
        data = json.loads(request.body)
        account_id = data.get('account_id')
        proxy_id = data.get('proxy_id')
        
        # Валидация входных данных
        if not account_id or proxy_id is None:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан ID аккаунта или Proxy ID'
            })
        
        # Проверяем что proxy_id является числом
        try:
            proxy_id = int(proxy_id)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Proxy ID должен быть числом'
            })
        
        # Обновляем proxy_id в базе данных
        with connection.cursor() as cursor:
            # Сначала проверяем существование аккаунта
            cursor.execute(
                'SELECT id_acc_bd FROM accs_data WHERE id_acc_bd = %s',
                [account_id]
            )
            
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': 'Аккаунт не найден'
                })
            
            # Обновляем proxy_id
            cursor.execute(
                'UPDATE accs_data SET proxy_id = %s WHERE id_acc_bd = %s',
                [proxy_id, account_id]
            )
            
            if cursor.rowcount > 0:
                return JsonResponse({
                    'success': True,
                    'message': f'Proxy ID успешно обновлен на {proxy_id}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось обновить Proxy ID'
                })
                
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректные данные JSON'
        })
    except Exception as e:
        logger.exception(f'Ошибка при обновлении proxy_id: {e}')
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })

@csrf_exempt
def add_rk_to_account(request):
    """Добавляет РК ID в список rk_list для аккаунта в таблице accs_data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        # Парсим JSON данные из тела запроса
        data = json.loads(request.body)
        account_id = data.get('account_id')
        rk_id = data.get('rk_id')
        
        # Валидация входных данных
        if not account_id or not rk_id:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан ID аккаунта или РК ID'
            })
        
        rk_id = str(rk_id).strip()
        
        # Работаем с базой данных
        with connection.cursor() as cursor:
            # Сначала проверяем существование аккаунта и получаем текущий rk_list
            cursor.execute(
                'SELECT id_acc_bd, rk_list FROM accs_data WHERE id_acc_bd = %s',
                [account_id]
            )
            
            row = cursor.fetchone()
            if not row:
                return JsonResponse({
                    'success': False,
                    'error': 'Аккаунт не найден'
                })
            
            current_rk_list = row[1]  # Получаем текущий rk_list
            
            # Обрабатываем rk_list
            if current_rk_list is None:
                # Если rk_list пустой, создаем новый список
                new_rk_list = [[rk_id, 'NEW']]
            else:
                # Если rk_list уже существует, проверяем, нет ли уже такого РК
                rk_ids = [rk[0] for rk in current_rk_list if len(rk) > 0]
                if rk_id in rk_ids:
                    return JsonResponse({
                        'success': False,
                        'error': 'Этот РК уже добавлен к аккаунту'
                    })
                
                # Добавляем новый РК к существующему списку
                new_rk_list = current_rk_list + [[rk_id, 'NEW']]
            
            # Обновляем rk_list в базе данных
            cursor.execute(
                'UPDATE accs_data SET rk_list = %s WHERE id_acc_bd = %s',
                [new_rk_list, account_id]
            )
            
            if cursor.rowcount > 0:
                return JsonResponse({
                    'success': True,
                    'message': f'РК {rk_id} успешно добавлен к аккаунту'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось обновить список РК'
                })
                
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректные данные JSON'
        })
    except Exception as e:
        logger.exception(f'Ошибка при добавлении РК: {e}')
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })

@csrf_exempt
def delete_rk_from_account(request):
    """Удаляет РК ID из списка rk_list для аккаунта в таблице accs_data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        # Парсим JSON данные из тела запроса
        data = json.loads(request.body)
        account_id = data.get('account_id')
        rk_id = data.get('rk_id')
        
        # Валидация входных данных
        if not account_id or not rk_id:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан ID аккаунта или РК ID'
            })
        
        rk_id = str(rk_id).strip()
        
        # Работаем с базой данных
        with connection.cursor() as cursor:
            # Сначала проверяем существование аккаунта и получаем текущий rk_list
            cursor.execute(
                'SELECT id_acc_bd, rk_list FROM accs_data WHERE id_acc_bd = %s',
                [account_id]
            )
            
            row = cursor.fetchone()
            if not row:
                return JsonResponse({
                    'success': False,
                    'error': 'Аккаунт не найден'
                })
            
            current_rk_list = row[1]  # Получаем текущий rk_list
            
            # Проверяем, что rk_list не пустой
            if not current_rk_list:
                return JsonResponse({
                    'success': False,
                    'error': 'Список РК пуст'
                })
            
            # Ищем РК в списке и удаляем его
            new_rk_list = []
            rk_found = False
            
            for rk in current_rk_list:
                if len(rk) > 0 and str(rk[0]) == rk_id:
                    rk_found = True
                    # Пропускаем этот РК (не добавляем в новый список)
                    continue
                else:
                    new_rk_list.append(rk)
            
            if not rk_found:
                return JsonResponse({
                    'success': False,
                    'error': 'РК не найден в списке аккаунта'
                })
            
            # Если список стал пустым, устанавливаем None
            if len(new_rk_list) == 0:
                final_rk_list = None
            else:
                final_rk_list = new_rk_list
            
            # Обновляем rk_list в базе данных
            cursor.execute(
                'UPDATE accs_data SET rk_list = %s WHERE id_acc_bd = %s',
                [final_rk_list, account_id]
            )
            
            if cursor.rowcount > 0:
                return JsonResponse({
                    'success': True,
                    'message': f'РК {rk_id} успешно удален с аккаунта'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось обновить список РК'
                })
                
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректные данные JSON'
        })
    except Exception as e:
        logger.exception(f'Ошибка при удалении РК: {e}')
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })

@csrf_exempt
def update_account_status(request):
    """Обновляет статус аккаунта в таблице accs_data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        # Парсим JSON данные из тела запроса
        data = json.loads(request.body)
        account_id = data.get('account_id')
        new_status = data.get('status')
        
        # Валидация входных данных
        if not account_id or not new_status:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан ID аккаунта или статус'
            })
        
        # Проверяем, что статус корректный
        allowed_statuses = ['ACTIVE', 'PendingUnban', 'BAN']
        if new_status not in allowed_statuses:
            return JsonResponse({
                'success': False,
                'error': 'Некорректный статус. Разрешены: ACTIVE, PendingUnban, BAN'
            })
        
        # Работаем с базой данных
        with connection.cursor() as cursor:
            # Сначала проверяем существование аккаунта
            cursor.execute(
                'SELECT id_acc_bd FROM accs_data WHERE id_acc_bd = %s',
                [account_id]
            )
            
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': 'Аккаунт не найден'
                })
            
            # Обновляем статус аккаунта
            cursor.execute(
                'UPDATE accs_data SET status = %s WHERE id_acc_bd = %s',
                [new_status, account_id]
            )
            
            if cursor.rowcount > 0:
                return JsonResponse({
                    'success': True,
                    'message': f'Статус аккаунта успешно изменен на {new_status}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось обновить статус аккаунта'
                })
                
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректные данные JSON'
        })
    except Exception as e:
        logger.exception(f'Ошибка при обновлении статуса аккаунта: {e}')
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })

@csrf_exempt
def update_account_token(request):
    """Обновляет токен аккаунта в таблице accs_data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        # Парсим JSON данные из тела запроса
        data = json.loads(request.body)
        account_id = data.get('account_id')
        new_token = data.get('token')
        
        # Валидация входных данных
        if not account_id or not new_token:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан ID аккаунта или токен'
            })
        
        new_token = new_token.strip()
        
        # Базовая валидация токена
        if len(new_token) < 50:
            return JsonResponse({
                'success': False,
                'error': 'Токен кажется слишком коротким. Проверьте правильность.'
            })
        
        # Работаем с базой данных
        with connection.cursor() as cursor:
            # Сначала проверяем существование аккаунта
            cursor.execute(
                'SELECT id_acc_bd FROM accs_data WHERE id_acc_bd = %s',
                [account_id]
            )
            
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': 'Аккаунт не найден'
                })
            
            # Обновляем токен аккаунта
            cursor.execute(
                'UPDATE accs_data SET token = %s WHERE id_acc_bd = %s',
                [new_token, account_id]
            )
            
            if cursor.rowcount > 0:
                return JsonResponse({
                    'success': True,
                    'message': 'Токен аккаунта успешно обновлен'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось обновить токен аккаунта'
                })
                
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректные данные JSON'
        })
    except Exception as e:
        logger.exception(f'Ошибка при обновлении токена аккаунта: {e}')
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })

@csrf_exempt
def update_fbt_acc_id(request):
    """Обновляет FBT ACC ID аккаунта в таблице accs_data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        # Парсим JSON данные из тела запроса
        data = json.loads(request.body)
        account_id = data.get('account_id')
        new_fbt_acc_id = data.get('fbt_acc_id')
        
        # Валидация входных данных
        if not account_id or new_fbt_acc_id is None:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан ID аккаунта или FBT ACC ID'
            })
        
        # Проверяем, что fbt_acc_id является числом
        try:
            fbt_acc_id_int = int(new_fbt_acc_id)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'FBT ACC ID должен быть числом'
            })
        
        # Работаем с базой данных
        with connection.cursor() as cursor:
            # Сначала проверяем существование аккаунта
            cursor.execute(
                'SELECT id_acc_bd FROM accs_data WHERE id_acc_bd = %s',
                [account_id]
            )
            
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': 'Аккаунт не найден'
                })
            
            # Обновляем fbt_acc_id аккаунта
            cursor.execute(
                'UPDATE accs_data SET fbt_acc_id = %s WHERE id_acc_bd = %s',
                [fbt_acc_id_int, account_id]
            )
            
            if cursor.rowcount > 0:
                return JsonResponse({
                    'success': True,
                    'message': 'FBT ACC ID успешно обновлен'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось обновить FBT ACC ID'
                })
                
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректные данные JSON'
        })
    except Exception as e:
        logger.exception(f'Ошибка при обновлении FBT ACC ID: {e}')
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })

@csrf_exempt
def update_dop_comment(request):
    """Обновляет дополнительный комментарий аккаунта в таблице accs_data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        # Парсим JSON данные из тела запроса
        data = json.loads(request.body)
        account_id = data.get('account_id')
        new_comment = data.get('dop_comment', '')
        
        # Валидация входных данных
        if not account_id:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан ID аккаунта'
            })
        
        # Обрезаем пробелы и ограничиваем длину комментария
        new_comment = new_comment.strip()
        if len(new_comment) > 1000:  # Ограничение в 1000 символов
            return JsonResponse({
                'success': False,
                'error': 'Комментарий слишком длинный (максимум 1000 символов)'
            })
        
        # Работаем с базой данных
        with connection.cursor() as cursor:
            # Сначала проверяем существование аккаунта
            cursor.execute(
                'SELECT id_acc_bd FROM accs_data WHERE id_acc_bd = %s',
                [account_id]
            )
            
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': 'Аккаунт не найден'
                })
            
            # Обновляем дополнительный комментарий аккаунта
            cursor.execute(
                'UPDATE accs_data SET dop_comment = %s WHERE id_acc_bd = %s',
                [new_comment, account_id]
            )
            
            if cursor.rowcount > 0:
                return JsonResponse({
                    'success': True,
                    'message': 'Дополнительный комментарий успешно обновлен'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось обновить комментарий'
                })
                
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректные данные JSON'
        })
    except Exception as e:
        logger.exception(f'Ошибка при обновлении дополнительного комментария: {e}')
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })

@csrf_exempt
def update_account_password(request):
    """Обновляет пароль аккаунта в таблице accs_data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        # Парсим JSON данные из тела запроса
        data = json.loads(request.body)
        account_id = data.get('account_id')
        new_password = data.get('password')
        
        # Валидация входных данных
        if not account_id or not new_password:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан ID аккаунта или пароль'
            })
        
        new_password = new_password.strip()
        
        # Базовая валидация пароля
        if len(new_password) < 1:
            return JsonResponse({
                'success': False,
                'error': 'Пароль не может быть пустым'
            })
        
        if len(new_password) > 255:
            return JsonResponse({
                'success': False,
                'error': 'Пароль слишком длинный (максимум 255 символов)'
            })
        
        # Работаем с базой данных
        with connection.cursor() as cursor:
            # Сначала проверяем существование аккаунта
            cursor.execute(
                'SELECT id_acc_bd FROM accs_data WHERE id_acc_bd = %s',
                [account_id]
            )
            
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': 'Аккаунт не найден'
                })
            
            # Обновляем пароль аккаунта
            cursor.execute(
                'UPDATE accs_data SET psw = %s WHERE id_acc_bd = %s',
                [new_password, account_id]
            )
            
            if cursor.rowcount > 0:
                return JsonResponse({
                    'success': True,
                    'message': 'Пароль аккаунта успешно обновлен'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось обновить пароль аккаунта'
                })
                
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректные данные JSON'
        })
    except Exception as e:
        logger.exception(f'Ошибка при обновлении пароля аккаунта: {e}')
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })

@csrf_exempt
def update_email_password(request):
    """Обновляет пароль от email в таблице accs_data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        # Парсим JSON данные из тела запроса
        data = json.loads(request.body)
        account_id = data.get('account_id')
        new_email_password = data.get('email_password')
        
        # Валидация входных данных
        if not account_id or not new_email_password:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан ID аккаунта или пароль от email'
            })
        
        new_email_password = new_email_password.strip()
        
        # Базовая валидация пароля
        if len(new_email_password) < 1:
            return JsonResponse({
                'success': False,
                'error': 'Пароль от email не может быть пустым'
            })
        
        if len(new_email_password) > 255:
            return JsonResponse({
                'success': False,
                'error': 'Пароль от email слишком длинный (максимум 255 символов)'
            })
        
        # Работаем с базой данных
        with connection.cursor() as cursor:
            # Сначала проверяем существование аккаунта
            cursor.execute(
                'SELECT id_acc_bd FROM accs_data WHERE id_acc_bd = %s',
                [account_id]
            )
            
            if not cursor.fetchone():
                return JsonResponse({
                    'success': False,
                    'error': 'Аккаунт не найден'
                })
            
            # Обновляем пароль от email
            cursor.execute(
                'UPDATE accs_data SET email_psw = %s WHERE id_acc_bd = %s',
                [new_email_password, account_id]
            )
            
            if cursor.rowcount > 0:
                return JsonResponse({
                    'success': True,
                    'message': 'Пароль от email успешно обновлен'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось обновить пароль от email'
                })
                
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректные данные JSON'
        })
    except Exception as e:
        logger.exception(f'Ошибка при обновлении пароля от email: {e}')
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })

@csrf_exempt
def update_rk_status(request, rk_id):
    """Обновляет статус рекламного кабинета в таблице rk_data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        # Получаем новый статус из POST данных
        new_status = request.POST.get('new_status')
        
        # Валидация входных данных
        if not new_status:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан новый статус'
            })
        
        new_status = new_status.strip()
        
        # Проверяем, что статус входит в допустимые значения
        allowed_statuses = ['NEW', 'WarmUp', 'READY', 'MOD', 'HOLD', 'ACTIVE', 'REJECTED', 'BAN', 'PAUSE', 'PendingUnban']
        if new_status not in allowed_statuses:
            return JsonResponse({
                'success': False,
                'error': f'Недопустимый статус. Разрешенные статусы: {", ".join(allowed_statuses)}'
            })
        
        # Работаем с базой данных
        with connection.cursor() as cursor:
            # Сначала проверяем существование РК
            cursor.execute(
                'SELECT id, rk_id FROM rk_data WHERE id = %s',
                [rk_id]
            )
            
            rk_data = cursor.fetchone()
            if not rk_data:
                return JsonResponse({
                    'success': False,
                    'error': 'Рекламный кабинет не найден'
                })
            
            # Обновляем статус РК
            cursor.execute(
                'UPDATE rk_data SET live_status = %s WHERE id = %s',
                [new_status, rk_id]
            )
            
            if cursor.rowcount > 0:
                logger.info(f'Статус РК id={rk_id} (rk_id={rk_data[1]}) обновлен на {new_status}')
                return JsonResponse({
                    'success': True,
                    'message': f'Статус РК успешно изменен на {new_status}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось обновить статус РК'
                })
                
    except Exception as e:
        logger.exception(f'Ошибка при обновлении статуса РК id={rk_id}: {e}')
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })


@csrf_exempt
def update_rk_comment(request, rk_id):
    """Обновляет комментарий рекламного кабинета в таблице rk_data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        # Получаем новый комментарий из POST данных
        new_comment = request.POST.get('new_comment')
        
        # Валидация входных данных
        if new_comment is None:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан комментарий'
            })
        
        new_comment = new_comment.strip()
        
        # Проверяем длину комментария
        if len(new_comment) > 500:
            return JsonResponse({
                'success': False,
                'error': 'Комментарий слишком длинный (максимум 500 символов)'
            })
        
        # Работаем с базой данных
        with connection.cursor() as cursor:
            # Сначала проверяем существование РК
            cursor.execute(
                'SELECT id, rk_id FROM rk_data WHERE id = %s',
                [rk_id]
            )
            
            rk_data = cursor.fetchone()
            if not rk_data:
                return JsonResponse({
                    'success': False,
                    'error': 'Рекламный кабинет не найден'
                })
            
            # Обновляем комментарий РК
            cursor.execute(
                'UPDATE rk_data SET comment = %s WHERE id = %s',
                [new_comment, rk_id]
            )
            
            if cursor.rowcount > 0:
                logger.info(f'Комментарий РК id={rk_id} (rk_id={rk_data[1]}) обновлен: {new_comment[:50]}...')
                return JsonResponse({
                    'success': True,
                    'message': 'Комментарий РК успешно обновлен'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось обновить комментарий РК'
                })
                
    except Exception as e:
        logger.exception(f'Ошибка при обновлении комментария РК id={rk_id}: {e}')
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })


@csrf_exempt
def update_pixel_id(request, rk_id):
    """Обновляет Pixel ID рекламного кабинета в таблице rk_data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        # Получаем новый Pixel ID из POST данных
        new_pixel_id = request.POST.get('new_pixel_id')
        
        # Валидация входных данных
        if new_pixel_id is None:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан Pixel ID'
            })
        
        new_pixel_id = new_pixel_id.strip()
        
        # Проверяем длину Pixel ID
        if len(new_pixel_id) > 255:
            return JsonResponse({
                'success': False,
                'error': 'Pixel ID слишком длинный (максимум 255 символов)'
            })
        
        # Работаем с базой данных
        with connection.cursor() as cursor:
            # Сначала проверяем существование РК
            cursor.execute(
                'SELECT id, rk_id FROM rk_data WHERE id = %s',
                [rk_id]
            )
            
            rk_data = cursor.fetchone()
            if not rk_data:
                return JsonResponse({
                    'success': False,
                    'error': 'Рекламный кабинет не найден'
                })
            
            # Обновляем Pixel ID РК
            cursor.execute(
                'UPDATE rk_data SET pixel_id = %s WHERE id = %s',
                [new_pixel_id, rk_id]
            )
            
            if cursor.rowcount > 0:
                logger.info(f'Pixel ID РК id={rk_id} (rk_id={rk_data[1]}) обновлен на: {new_pixel_id}')
                return JsonResponse({
                    'success': True,
                    'message': 'Pixel ID успешно обновлен'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось обновить Pixel ID'
                })
                
    except Exception as e:
        logger.exception(f'Ошибка при обновлении Pixel ID РК id={rk_id}: {e}')
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })


@csrf_exempt
def update_pixel_token(request, rk_id):
    """Обновляет Pixel Token рекламного кабинета в таблице rk_data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        # Получаем новый Pixel Token из POST данных
        new_pixel_token = request.POST.get('new_pixel_token')
        
        # Валидация входных данных
        if new_pixel_token is None:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан Pixel Token'
            })
        
        new_pixel_token = new_pixel_token.strip()
        
        # Проверяем длину Pixel Token
        if len(new_pixel_token) > 500:
            return JsonResponse({
                'success': False,
                'error': 'Pixel Token слишком длинный (максимум 500 символов)'
            })
        
        # Работаем с базой данных
        with connection.cursor() as cursor:
            # Сначала проверяем существование РК
            cursor.execute(
                'SELECT id, rk_id FROM rk_data WHERE id = %s',
                [rk_id]
            )
            
            rk_data = cursor.fetchone()
            if not rk_data:
                return JsonResponse({
                    'success': False,
                    'error': 'Рекламный кабинет не найден'
                })
            
            # Обновляем Pixel Token РК
            cursor.execute(
                'UPDATE rk_data SET pixel_token = %s WHERE id = %s',
                [new_pixel_token, rk_id]
            )
            
            if cursor.rowcount > 0:
                logger.info(f'Pixel Token РК id={rk_id} (rk_id={rk_data[1]}) обновлен на: {new_pixel_token[:50]}...')
                return JsonResponse({
                    'success': True,
                    'message': 'Pixel Token успешно обновлен'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось обновить Pixel Token'
                })
                
    except Exception as e:
        logger.exception(f'Ошибка при обновлении Pixel Token РК id={rk_id}: {e}')
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })


@csrf_exempt
def update_acc_id(request, rk_id):
    """Обновляет ACC ID рекламного кабинета в таблице rk_data"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        # Получаем новый ACC ID из POST данных
        new_acc_id = request.POST.get('new_acc_id')
        
        # Валидация входных данных
        if not new_acc_id:
            return JsonResponse({
                'success': False, 
                'error': 'Не указан ACC ID'
            })
        
        new_acc_id = new_acc_id.strip()
        
        # Проверяем, что введенное значение - это целое число
        try:
            new_acc_id = int(new_acc_id)
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'ACC ID должен быть целым числом'
            })
        
        # Работаем с базой данных
        with connection.cursor() as cursor:
            # Сначала проверяем существование РК
            cursor.execute(
                'SELECT id, rk_id FROM rk_data WHERE id = %s',
                [rk_id]
            )
            
            rk_data = cursor.fetchone()
            if not rk_data:
                return JsonResponse({
                    'success': False,
                    'error': 'Рекламный кабинет не найден'
                })
            
            # Обновляем ACC ID РК
            cursor.execute(
                'UPDATE rk_data SET id_acc_bd = %s WHERE id = %s',
                [new_acc_id, rk_id]
            )
            
            if cursor.rowcount > 0:
                logger.info(f'ACC ID РК id={rk_id} (rk_id={rk_data[1]}) обновлен на: {new_acc_id}')
                return JsonResponse({
                    'success': True,
                    'message': f'ACC ID успешно обновлен на {new_acc_id}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось обновить ACC ID'
                })
                
    except Exception as e:
        logger.exception(f'Ошибка при обновлении ACC ID РК id={rk_id}: {e}')
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })

@csrf_exempt
@login_required
def save_report(request):
    """Сохранение отчета пользователя"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        data = json.loads(request.body)
        report_name = data.get('report_name')
        
        if not report_name:
            return JsonResponse({'success': False, 'error': 'Название отчета обязательно'})
        
        # Создаем или обновляем отчет
        try:
            with connection.cursor() as cursor:
                # Проверяем, существует ли отчет
                cursor.execute("""
                    SELECT COUNT(*) FROM users_report_data 
                    WHERE user_id = %s AND report_name = %s
                """, [request.user.id, report_name])
                
                exists = cursor.fetchone()[0] > 0
                
                # Подготавливаем данные для PostgreSQL массивов
                columns_array = data.get('columns', [])
                filters_array = data.get('filters', [])
                
                # Для reports_structure_list - массив строк
                columns_pg_array = '{' + ','.join([f'"{col}"' for col in columns_array]) + '}'
                
                # Для report_filters - массив JSON объектов
                filters_pg_array = '{' + ','.join([json.dumps(filter_obj).replace('"', '\\"') for filter_obj in filters_array]) + '}'
                
                if exists:
                    # Обновляем существующий отчет
                    cursor.execute("""
                        UPDATE users_report_data 
                        SET reports_structure_list = %s::character varying[], report_filters = %s::json[], report_dates = %s
                        WHERE user_id = %s AND report_name = %s
                    """, [
                        columns_pg_array,
                        filters_pg_array,
                        data.get('date_range', ''),
                        request.user.id,
                        report_name
                    ])
                    action = 'обновлен'
                else:
                    # Создаем новый отчет
                    cursor.execute("""
                        INSERT INTO users_report_data (user_id, report_name, reports_structure_list, report_filters, report_dates)
                        VALUES (%s, %s, %s::character varying[], %s::json[], %s)
                    """, [
                        request.user.id,
                        report_name,
                        columns_pg_array,
                        filters_pg_array,
                        data.get('date_range', '')
                    ])
                    action = 'создан'
                
                return JsonResponse({
                    'success': True, 
                    'message': f'Отчет "{report_name}" {action}',
                    'report_name': report_name
                })
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Ошибка сохранения: {str(e)}'})
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Неверный формат данных'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@login_required
def load_report(request, report_name):
    """Загрузка сохраненного отчета"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT report_name, reports_structure_list, report_filters, report_dates
                FROM users_report_data 
                WHERE user_id = %s AND report_name = %s
            """, [request.user.id, report_name])
            
            row = cursor.fetchone()
            if not row:
                return JsonResponse({'success': False, 'error': 'Отчет не найден'})
            
            # Парсим PostgreSQL массивы
            # reports_structure_list - character varying[]
            reports_structure_list = row[1] if row[1] else []
            # report_filters - json[]
            report_filters = row[2] if row[2] else []
            
            return JsonResponse({
                'success': True,
                'report': {
                    'name': row[0],
                    'columns': reports_structure_list,
                    'filters': report_filters,
                    'date_range': row[3] or '',
                }
            })
    except Exception as e:
        logger.error(f'Ошибка загрузки отчета {report_name}: {e}')
        return JsonResponse({'success': False, 'error': f'Ошибка загрузки: {str(e)}'})


@csrf_exempt
@login_required
def delete_report(request, report_name):
    """Удаление сохраненного отчета"""
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM users_report_data 
                WHERE user_id = %s AND report_name = %s
            """, [request.user.id, report_name])
            
            if cursor.rowcount == 0:
                return JsonResponse({'success': False, 'error': 'Отчет не найден'})
            
            return JsonResponse({
                'success': True, 
                'message': f'Отчет "{report_name}" удален'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
