# wms_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # API 및 엑셀 업로드 URL
    path('order/excel_upload/', views.order_excel_upload, name='order_excel_upload'),
    path('api/orders/', views.order_list_api, name='order_list_api'),
    path('api/check-username/', views.check_username, name='check_username'),
    path('api/order-chart/', views.order_chart_data, name='order_chart_data'),
    path('api/delivery-chart/', views.delivery_chart_data, name='delivery_chart_data'),
    path('api/channel-order-chart/', views.channel_order_chart_data, name='channel_order_chart_data'),

    # --- [수정] 아래 한 줄이 홈 화면(대시보드)을 정의하는 가장 중요한 부분입니다. ---
    path('', views.dashboard, name='dashboard'),
    # --------------------------------------------------------------------

    # Order (주문)
    path('order/manage/', views.order_manage, name='order_manage'),
    path('order/list/success/', views.order_list_success, name='order_list_success'),
    path('order/list/error/', views.order_list_error, name='order_list_error'),
    path('order/<int:order_pk>/update/', views.order_update_view, name='order_update'),

    # In/Out (입출고)
    path('stock/in/', views.stock_in, name='stock_in'),
    path('stock/out/', views.stock_out, name='stock_out'),
    path('stock/io/', views.stock_io_view, name='stock_io'),
    path('stock/history/', views.stock_movement_history, name='stock_history'),
    
    # Settlement (정산)
    path('settlement/status/', views.settlement_status, name='settlement_status'),
    path('settlement/billing/', views.settlement_billing, name='settlement_billing'),
    path('settlement/config/', views.settlement_config, name='settlement_config'),
    
    # Management (관리)
    path('management/dashboard/', views.management_dashboard, name='management_dashboard'),
    path('management/orders/', views.order_manage_new, name='order_manage_new'),
    path('management/stock/', views.stock_manage, name='stock_manage'),
    path('management/users/', views.user_manage, name='user_manage'),
    path('management/users/<int:pk>/update/', views.user_update, name='user_update'),
    path('stock/<int:pk>/update/', views.stock_update, name='stock_update'),

    # Settings - Center (센터 설정)
    path('settings/centers/', views.CenterListView.as_view(), name='center_list'),
    path('settings/centers/new/', views.CenterCreateView.as_view(), name='center_create'),
    path('settings/centers/<int:pk>/edit/', views.CenterUpdateView.as_view(), name='center_update'),
    path('settings/centers/<int:pk>/delete/', views.CenterDeleteView.as_view(), name='center_delete'),

    # Settings - Shipper (화주사 설정)
    path('settings/shippers/', views.ShipperListView.as_view(), name='shipper_list'),
    path('settings/shippers/new/', views.ShipperCreateView.as_view(), name='shipper_create'),
    path('settings/shippers/<int:pk>/edit/', views.ShipperUpdateView.as_view(), name='shipper_update'),
    path('settings/shippers/<int:pk>/delete/', views.ShipperDeleteView.as_view(), name='shipper_delete'),

    # Settings - Courier (택배사 설정)
    path('settings/couriers/', views.CourierListView.as_view(), name='courier_list'),
    path('settings/couriers/new/', views.CourierCreateView.as_view(), name='courier_create'),
    path('settings/couriers/<int:pk>/edit/', views.CourierUpdateView.as_view(), name='courier_update'),
    path('settings/couriers/<int:pk>/delete/', views.CourierDeleteView.as_view(), name='courier_delete'),

    # Shipper Products (화주사별 상품)
    path('shippers/<int:shipper_pk>/products/', views.shipper_product_list, name='shipper_product_list'),
    path('shippers/<int:shipper_pk>/products/new/', views.shipper_product_create, name='shipper_product_create'),
    path('products/<int:pk>/edit/', views.shipper_product_update, name='shipper_product_update'),
    path('products/<int:pk>/delete/', views.shipper_product_delete, name='shipper_product_delete'),
]