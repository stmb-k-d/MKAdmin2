from django.shortcuts import render, redirect
from django.db import connection
from .models import MenuItem, Campaign, AdSet, Ad, Proxy
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
import sys
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

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
    ]

def index(request):
    return render(request, 'dashboard/index.html', {
        'menu_items': get_menu_items(),
        'title': 'Главная',
        'page_title': 'Панель управления'
    })

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

def check_proxy(request, proxy_id):
    try:
        proxy = Proxy.objects.get(id=proxy_id)
        # Здесь будет логика проверки прокси
        return JsonResponse({'success': True})
    except Proxy.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Прокси не найден'})

def delete_proxy(request, proxy_id):
    try:
        proxy = Proxy.objects.get(id=proxy_id)
        proxy.delete()
        return JsonResponse({'success': True})
    except Proxy.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Прокси не найден'})

def count_free_proxies(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM proxy_data WHERE accs IS NULL')
        count = cursor.fetchone()[0]
    return JsonResponse({'count': count})

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

def accs_detail(request, account_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM accs_data WHERE id_acc_bd = %s", [account_id])
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        if row:
            account = dict(zip(columns, row))
        else:
            account = None

    context = {
        'menu_items': get_menu_items(),
        'title': 'Детали аккаунта',
        'page_title': 'Детали аккаунта',
        'account': account,
    }
    return render(request, 'dashboard/accs_detail.html', context)

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

def statistic_view(request):
    return render(request, 'dashboard/statistic.html', {
        'menu_items': get_menu_items(),
        'title': 'Статистика',
        'page_title': 'Статистика'
    })

def analytics_view(request):
    return render(request, 'dashboard/analytics.html', {
        'menu_items': get_menu_items(),
        'title': 'Аналитика',
        'page_title': 'Аналитика'
    })

def tasks_view(request):
    return render(request, 'dashboard/tasks.html', {
        'menu_items': get_menu_items(),
        'title': 'Задачи',
        'page_title': 'Управление задачами'
    })

def finance_view(request):
    return render(request, 'dashboard/finance.html', {
        'menu_items': get_menu_items(),
        'title': 'Финансы',
        'page_title': 'Финансы'
    })

def services_view(request):
    return render(request, 'dashboard/services.html', {
        'menu_items': get_menu_items(),
        'title': 'Сервисы',
        'page_title': 'Управление сервисами'
    })

def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html', {
        'menu_items': get_menu_items(),
        'title': 'Дашборд',
        'page_title': 'Главная страница'
    })

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

def campaigns(request):
    return render(request, 'dashboard/campaigns.html', {
        'menu_items': get_menu_items()
    })

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
    
    return render(request, 'dashboard/ad_detail.html', {
        'menu_items': get_menu_items(),
        'title': f'Ad Detail: {ad_id}',
        'page_title': f'Объявление: {ad_id}',
        'ad': ad,
        'daily_stats': daily_stats,
        'back_url': back_url,
        'back_text': back_text
    })

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
                        # Пытаемся распарсить datetime
                        try:
                            if hasattr(row[i], 'strftime'):
                                item[col] = row[i].strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                item[col] = str(row[i])
                        except:
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

def facebook_stats_view(request):
    """
    Отображает данные статистики Facebook из таблицы ad_data_daily
    """
    try:
        # Получаем параметры фильтрации по датам из запроса
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
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
            
            return render(request, 'dashboard/facebook_stats.html', {
                'data': data,
                'columns': columns,
                'menu_items': get_menu_items(),
                'title': 'Facebook Statistics',
                'page_title': 'Статистика Facebook',
                'date_from': date_from,
                'date_to': date_to
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
