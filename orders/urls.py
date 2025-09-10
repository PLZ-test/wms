# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # 주문 관리 페이지
    path('manage/', views.order_manage_view, name='manage'),
    
    # 주문 목록 (성공/오류)
    path('list/success/<str:date_str>/', views.order_list_success_view, name='list_success'),
    path('list/error/<str:date_str>/', views.order_list_error_view, name='list_error'),
    
    # 오류 주문 수정 및 송장 출력
    path('<int:order_pk>/update/', views.order_update_view, name='update'),
    path('invoice/', views.order_invoice_view, name='invoice'),

    # --- API URLS ---
    # 엑셀 처리 관련
    path('api/process_excel/', views.process_orders_api, name='process_excel_api'),
    path('api/batch_retry/', views.batch_retry_error_api, name='batch_retry_error_api'),
    
    # 자동완성
    path('api/products/autocomplete/', views.product_autocomplete_api, name='product_autocomplete_api'),
    
    # 차트 데이터
    path('api/order-chart/', views.order_chart_data_api, name='chart_data'),
    path('api/channel-order-chart/', views.channel_order_chart_data_api, name='channel_chart_data'),
]