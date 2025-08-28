# plz-test/wms/wms-569b83abab27982f84c8119e40d23c3d187118cc/wms_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # 엑셀 처리 API
    path('api/orders/check_duplicates/', views.check_duplicates_api, name='check_duplicates_api'),
    path('api/orders/process_excel/', views.process_orders_api, name='process_orders_api'),
    
    # --- [수정] 기존 단일 재처리 API 삭제 후, 새로운 일괄 처리 API URL 추가 ---
    path('api/orders/batch_retry/', views.batch_retry_error_api, name='batch_retry_error_api'),
    # ------------------------------------------------------------------

    # 기존 URL
    path('order/invoice/', views.order_invoice_view, name='order_invoice'),
    path('api/check-username/', views.check_username, name='check_username'),
    path('api/order-chart/', views.order_chart_data, name='order_chart_data'),
    path('api/channel-order-chart/', views.channel_order_chart_data, name='channel_order_chart_data'),

    path('', views.dashboard, name='dashboard'),

    # Order (주문)
    path('order/manage/', views.order_manage, name='order_manage'),
    path('order/list/success/<str:date_str>/', views.order_list_success, name='order_list_success'),
    path('order/list/error/<str:date_str>/', views.order_list_error, name='order_list_error'),
    path('order/list/error/<str:date_str>/download/', views.download_error_excel, name='download_error_excel'),
    
    path('order/<int:order_pk>/update/', views.order_update_view, name='order_update'),

    # (이하 나머지 URL은 변경 없음)
    path('stock/in/', views.stock_in, name='stock_in'),
    path('stock/out/', views.stock_out, name='stock_out'),
    path('stock/io/', views.stock_io_view, name='stock_io'),
    path('stock/history/', views.stock_movement_history, name='stock_history'),
    path('settlement/status/', views.settlement_status, name='settlement_status'),
    path('settlement/billing/', views.settlement_billing, name='settlement_billing'),
    path('settlement/config/', views.settlement_config, name='settlement_config'),
    path('management/dashboard/', views.management_dashboard, name='management_dashboard'),
    path('management/orders/', views.order_manage_new, name='order_manage_new'),
    path('management/stock/', views.stock_manage, name='stock_manage'),
    path('management/users/', views.user_manage, name='user_manage'),
    path('management/users/<int:pk>/update/', views.user_update, name='user_update'),
    path('stock/<int:pk>/update/', views.stock_update, name='stock_update'),
    path('settings/centers/', views.CenterListView.as_view(), name='center_list'),
    path('settings/centers/new/', views.CenterCreateView.as_view(), name='center_create'),
    path('settings/centers/<int:pk>/edit/', views.CenterUpdateView.as_view(), name='center_update'),
    path('settings/centers/<int:pk>/delete/', views.CenterDeleteView.as_view(), name='center_delete'),
    path('settings/shippers/', views.ShipperListView.as_view(), name='shipper_list'),
    path('settings/shippers/new/', views.ShipperCreateView.as_view(), name='shipper_create'),
    path('settings/shippers/<int:pk>/edit/', views.ShipperUpdateView.as_view(), name='shipper_update'),
    path('settings/shippers/<int:pk>/delete/', views.ShipperDeleteView.as_view(), name='shipper_delete'),
    path('settings/couriers/', views.CourierListView.as_view(), name='courier_list'),
    path('settings/couriers/new/', views.CourierCreateView.as_view(), name='courier_create'),
    path('settings/couriers/<int:pk>/edit/', views.CourierUpdateView.as_view(), name='courier_update'),
    path('settings/couriers/<int:pk>/delete/', views.CourierDeleteView.as_view(), name='courier_delete'),
    path('shippers/<int:shipper_pk>/products/', views.shipper_product_list, name='shipper_product_list'),
    path('shippers/<int:shipper_pk>/products/new/', views.shipper_product_create, name='shipper_product_create'),
    path('products/<int:pk>/edit/', views.shipper_product_update, name='shipper_product_update'),
    path('products/<int:pk>/delete/', views.shipper_product_delete, name='shipper_product_delete'),
]