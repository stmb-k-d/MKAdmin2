from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('proxy/', views.proxy, name='proxy'),
    path('proxy/<int:proxy_id>/', views.proxy_detail, name='proxy_detail'),
    path('proxy/check/<int:proxy_id>/', views.check_proxy, name='check_proxy'),
    path('proxy/delete/<int:proxy_id>/', views.delete_proxy, name='delete_proxy'),
    path('proxy/count-free/', views.count_free_proxies, name='count_free_proxies'),
    path('accs/', views.accs_view, name='accs'),
    path('accs/<int:account_id>/', views.accs_detail, name='accs_detail'),
    path('rk/', views.rk_view, name='rk'),
    path('rk/<int:rk_id>/', views.rk_detail, name='rk_detail'),
    path('campaigns/', views.campaigns, name='campaigns'),
    path('adsets/', views.adsets, name='adsets'),
    path('ads/', views.ads, name='ads'),
    path('ad/update_kt_campaign_id/<str:ad_id>/', views.update_kt_campaign_id, name='update_kt_campaign_id'),
    path('ad/update_id_acc_bd/<str:ad_id>/', views.update_id_acc_bd, name='update_id_acc_bd'),
    path('ad/<str:ad_id>/', views.ad_detail, name='ad_detail'),
    path('statistic/', views.statistic_view, name='statistic'),
    path('statistic/facebook/', views.facebook_stats_view, name='facebook_stats'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('finance/', views.finance_view, name='finance'),
    path('services/', views.services_view, name='services'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('working_log/', views.working_log, name='working_log'),
    path('api/facebook/stats/data/', views.get_facebook_stats_data, name='facebook_stats_data'),
    path('api/facebook/stats/chart/', views.get_facebook_stats_chart_data, name='facebook_stats_chart'),
] 