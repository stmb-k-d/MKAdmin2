from django.shortcuts import render, redirect
from django.db import connection
from .models import MenuItem, Campaign, AdSet, Ad, Proxy
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def get_menu_items():
    return [
        {'name': 'dashboard', 'title': 'Дашборд', 'icon': 'fas fa-tachometer-alt'},
        {'name': 'proxy', 'title': 'Прокси', 'icon': 'fas fa-server'},
        {'name': 'accs', 'title': 'Аккаунты', 'icon': 'fas fa-users'},
        {'name': 'rk', 'title': 'РК', 'icon': 'fas fa-chart-line'},
        {'name': 'statistic', 'title': 'Статистика', 'icon': 'fas fa-chart-bar'},
        {'name': 'analytics', 'title': 'Аналитика', 'icon': 'fas fa-chart-pie'},
        {'name': 'tasks', 'title': 'Задачи', 'icon': 'fas fa-tasks'},
        {'name': 'finance', 'title': 'Финансы', 'icon': 'fas fa-money-bill-wave'},
        {'name': 'services', 'title': 'Сервисы', 'icon': 'fas fa-cogs'},
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
                last_update,
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
