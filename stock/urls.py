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
    path('outbound/', views.stock_out_view, name='out_bound'),
    path('history/', views.stock_movement_history_view, name='history'),

    # 재고 위치(구역) 관리
    path('location/manage/', views.location_manage_view, name='location_manage'),
    path('location/<int:pk>/update/', views.location_update_view, name='location_update'),
    path('location/<int:pk>/delete/', views.location_delete_view, name='location_delete'),

    # --- [삭제] 더 이상 사용하지 않는 기본 위치 생성 URL을 삭제합니다. ---
    # path('location/create-defaults/', views.location_create_defaults_view, name='location_create_defaults'),

    # API
    path('api/chart-data/', views.stock_chart_data_api, name='chart_data_api'),
    path('api/shipper-stock-chart/', views.shipper_stock_chart_api, name='shipper_stock_chart'),

    # 대시보드 (신규)
    path('dashboard/', views.stock_dashboard_view, name='dashboard'),
]