# stock/urls.py
from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    # 재고 현황 (관리 메뉴에 속함)
    path('manage/', views.stock_manage_view, name='manage'),
    path('manage/<int:pk>/update/', views.stock_update_view, name='update'),

    # 재고 입출고 (입출고 메뉴에 속함)
    path('io/', views.stock_io_view, name='io'),
    path('history/', views.stock_movement_history_view, name='history'),
]