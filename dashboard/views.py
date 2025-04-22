from django.shortcuts import render, redirect
from django.db import connection
from .models import MenuItem, Campaign, AdSet, Ad, Proxy
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
import sys

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
        {'name': 'analytics', 'title': 'Аналитика', 'icon': 'fas fa-chart-pie'},
        {'name': 'tasks', 'title': 'Задачи', 'icon': 'fas fa-tasks'},
        {'name': 'finance', 'title': 'Финансы', 'icon': 'fas fa-money-bill-wave'},
        {'name': 'services', 'title': 'Сервисы', 'icon': 'fas fa-cogs'},
        {'name': 'working_log', 'title': 'Working Log', 'icon': 'fas fa-clipboard-list'},
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
    
    return render(request, 'dashboard/accs.html', {
        'menu_items': get_menu_items(),
        'title': 'Аккаунты',
        'page_title': 'Управление аккаунтами',
        'accounts': accounts
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
    return render(request, 'dashboard/adsets.html', {
        'menu_items': get_menu_items()
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
        'page_title': f'Детали объявления: {ad_id}',
        'ad': ad,
        'daily_stats': daily_stats
    })

def working_log(request):
    return render(request, 'dashboard/working_log.html', {
        'page_title': 'Working Log',
        'menu_items': get_menu_items()
    })

def facebook_stats_view(request):
    """
    Отображает демо-данные для статистики Facebook
    из-за проблем с доступом к таблице ad_data_daily
    """
    import sys
    print("================ НАЧАЛО ФУНКЦИИ FACEBOOK_STATS_VIEW (УПРОЩЕННАЯ) ================", file=sys.stderr)
    
    # Принудительно создаем демо-данные без попыток проверить таблицу
    return generate_demo_stats_data(request, ["Принудительно загружены демо-данные для демонстрации функциональности"])

def generate_demo_stats_data(request, errors=None):
    """
    Создает демонстрационные данные для отображения на странице статистики
    
    Args:
        request: HTTP-запрос
        errors: список ошибок для отображения на странице
    """
    import random
    import sys
    from datetime import datetime, timedelta
    
    print("================ НАЧАЛО ГЕНЕРАЦИИ ДЕМО-ДАННЫХ ================", file=sys.stderr)
    
    # Создаем список колонок, аналогичный структуре таблицы ad_data_daily
    columns = [
        'id', 'date_log', 'ad_id', 'fb_spend', 'fb_impressions', 'fb_clicks', 
        'fb_ctr', 'fb_cpc', 'fb_cpm', 'fb_link_click', 'fb_cost_per_unique_click',
        'kt_unic_clicks', 'c2i', 'cr2i', 'cpi', 'regs', 'cr2r', 'i2r', 'cpr',
        'cr2d', 'r2s', 'cps', 'deps', 'income', 'bprofit', 'broi'
    ]
    
    # Создаем 10 случайных ad_id
    ad_ids = [f"2318900{i}556{i+2}" for i in range(10)]
    
    # Создаем даты за последние 30 дней
    end_date = datetime.now()
    dates = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
    
    # Создаем демо-данные
    stats_data = []
    id_counter = 1
    
    print(f"Генерируем данные для {len(ad_ids)} объявлений и {len(dates)} дат", file=sys.stderr)
    
    for ad_id in ad_ids:
        for date in dates:
            # Базовые метрики
            spend = round(random.uniform(10, 100), 2)
            impressions = random.randint(1000, 10000)
            clicks = random.randint(10, impressions // 50)
            
            # Расчетные метрики
            ctr = round((clicks / impressions) * 100, 2) if impressions > 0 else 0
            cpc = round(spend / clicks, 2) if clicks > 0 else 0
            cpm = round((spend / impressions) * 1000, 2) if impressions > 0 else 0
            
            link_clicks = int(clicks * random.uniform(0.8, 1.0))
            cost_per_unique_click = round(spend / (link_clicks * random.uniform(0.8, 0.95)), 2) if link_clicks > 0 else 0
            
            kt_unic_clicks = int(link_clicks * random.uniform(0.8, 0.95))
            c2i = int(kt_unic_clicks * random.uniform(0.1, 0.4))
            cr2i = round((c2i / kt_unic_clicks) * 100, 2) if kt_unic_clicks > 0 else 0
            cpi = round(spend / c2i, 2) if c2i > 0 else 0
            
            regs = int(c2i * random.uniform(0.5, 0.9))
            cr2r = round((regs / clicks) * 100, 2) if clicks > 0 else 0
            i2r = round((regs / c2i) * 100, 2) if c2i > 0 else 0
            cpr = round(spend / regs, 2) if regs > 0 else 0
            
            deps = int(regs * random.uniform(0.1, 0.4))
            cr2d = round((deps / clicks) * 100, 2) if clicks > 0 else 0
            r2s = round((deps / regs) * 100, 2) if regs > 0 else 0
            cps = round(spend / deps, 2) if deps > 0 else 0
            
            income = round(deps * random.uniform(50, 200), 2)
            bprofit = round(income - spend, 2)
            broi = round((bprofit / spend) * 100, 2) if spend > 0 else 0
            
            # Создаем запись
            stats_data.append({
                'id': id_counter,
                'date_log': date,
                'ad_id': ad_id,
                'fb_spend': spend,
                'fb_impressions': impressions,
                'fb_clicks': clicks,
                'fb_ctr': ctr,
                'fb_cpc': cpc,
                'fb_cpm': cpm,
                'fb_link_click': link_clicks,
                'fb_cost_per_unique_click': cost_per_unique_click,
                'kt_unic_clicks': kt_unic_clicks,
                'c2i': c2i,
                'cr2i': cr2i,
                'cpi': cpi,
                'regs': regs,
                'cr2r': cr2r,
                'i2r': i2r,
                'cpr': cpr,
                'cr2d': cr2d,
                'r2s': r2s,
                'cps': cps,
                'deps': deps,
                'income': income,
                'bprofit': bprofit,
                'broi': broi
            })
            id_counter += 1
    
    print(f"Сгенерировано {len(stats_data)} записей", file=sys.stderr)
    print("================ КОНЕЦ ГЕНЕРАЦИИ ДЕМО-ДАННЫХ ================", file=sys.stderr)
    
    return render(request, 'dashboard/facebook_stats.html', {
        'menu_items': get_menu_items(),
        'title': 'Facebook Stats (Demo)',
        'page_title': 'Статистика Facebook (Демо-данные)',
        'stats_data': stats_data,
        'columns': columns,
        'dates': dates,
        'ad_ids': ad_ids,
        'is_demo': True,
        'errors': errors
    })
