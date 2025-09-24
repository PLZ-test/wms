# stock/urls.py
from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    # 재고 현황
    path('manage/', views.stock_manage_view, name='manage'),
    path('manage/<int:pk>/update/', views.stock_update_view, name='update'),

    # 입고 및 기록
    path('inbound/', views.stock_in_view, name='in_bound'),
    path('history/', views.stock_movement_history_view, name='history'),

    # 도면 관리
    path('layout/manage/', views.layout_manage_view, name='layout_manage'), # [신규]
    path('layout/<int:layout_id>/edit/', views.layout_editor_view, name='layout_editor'),

    # API
    path('api/chart-data/', views.stock_chart_data_api, name='chart_data_api'),
    path('api/layout/<int:layout_id>/locations/', views.location_api, name='location_api'),
]