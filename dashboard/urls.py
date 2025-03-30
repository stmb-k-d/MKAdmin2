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
    path('statistic/', views.statistic_view, name='statistic'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('finance/', views.finance_view, name='finance'),
    path('services/', views.services_view, name='services'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
] 