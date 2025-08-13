from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # --- [추가] 인증 관련 URL ---
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/done/', views.signup_done_view, name='signup_done'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('api/order-chart/', views.order_chart_data, name='order_chart_data'),
    path('api/delivery-chart/', views.delivery_chart_data, name='delivery_chart_data'),

    # Order
    path('order/manage/', views.order_manage, name='order_manage'),

    # In/Out
    path('stock/in/', views.stock_in, name='stock_in'),
    path('stock/out/', views.stock_out, name='stock_out'),
    path('stock/io/', views.stock_io_view, name='stock_io'),
    path('stock/history/', views.stock_movement_history, name='stock_history'),
    
    # Settlement
    path('settlement/status/', views.settlement_status, name='settlement_status'),
    path('settlement/billing/', views.settlement_billing, name='settlement_billing'),
    path('settlement/config/', views.settlement_config, name='settlement_config'),
    
    # Management
    path('management/orders/', views.order_manage_new, name='order_manage_new'),
    path('management/stock/', views.stock_manage, name='stock_manage'),
    
    path('management/users/', views.user_manage, name='user_manage'),
    path('management/users/<int:pk>/update/', views.user_update, name='user_update'),
    
    path('management/shippers/', views.ShipperListView.as_view(), name='shipper_list'),
    path('stock/<int:pk>/update/', views.stock_update, name='stock_update'),

    # Settings - Center
    path('settings/centers/', views.CenterListView.as_view(), name='center_list'),
    path('settings/centers/new/', views.CenterCreateView.as_view(), name='center_create'),
    path('settings/centers/<int:pk>/edit/', views.CenterUpdateView.as_view(), name='center_update'),
    path('settings/centers/<int:pk>/delete/', views.CenterDeleteView.as_view(), name='center_delete'),

    # Settings - Shipper
    path('settings/shippers/new/', views.ShipperCreateView.as_view(), name='shipper_create'),
    path('settings/shippers/<int:pk>/edit/', views.ShipperUpdateView.as_view(), name='shipper_update'),
    path('settings/shippers/<int:pk>/delete/', views.ShipperDeleteView.as_view(), name='shipper_delete'),

    # Settings - Courier
    path('settings/couriers/', views.CourierListView.as_view(), name='courier_list'),
    path('settings/couriers/new/', views.CourierCreateView.as_view(), name='courier_create'),
    path('settings/couriers/<int:pk>/edit/', views.CourierUpdateView.as_view(), name='courier_update'),
    path('settings/couriers/<int:pk>/delete/', views.CourierDeleteView.as_view(), name='courier_delete'),

    # Shipper Products
    path('shippers/<int:shipper_pk>/products/', views.shipper_product_list, name='shipper_product_list'),
    path('shippers/<int:shipper_pk>/products/new/', views.shipper_product_create, name='shipper_product_create'),
    path('products/<int:pk>/edit/', views.shipper_product_update, name='shipper_product_update'),
    path('products/<int:pk>/delete/', views.shipper_product_delete, name='shipper_product_delete'),
]