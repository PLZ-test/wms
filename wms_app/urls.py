from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('api/order-chart/', views.order_chart_data, name='order_chart_data'),
    path('api/delivery-chart/', views.delivery_chart_data, name='delivery_chart_data'),

    # Orders (Placeholder pages)
    path('orders/collect/', views.order_collect, name='order_collect'),
    path('orders/match/', views.order_match, name='order_match'),
    path('orders/combine/', views.order_combine, name='order_combine'),
    path('orders/invoice/', views.order_invoice, name='order_invoice'),
    path('orders/manage/', views.order_manage, name='order_manage'),
    
    # Stock
    path('stock/manage/', views.stock_manage, name='stock_manage'),
    path('stock/io/', views.stock_io_view, name='stock_io'),
    path('stock/<int:pk>/update/', views.stock_update, name='stock_update'),
    path('stock/history/', views.stock_movement_history, name='stock_history'),

    # Settlement (Placeholder pages)
    path('settlement/status/', views.settlement_status, name='settlement_status'),
    path('settlement/billing/', views.settlement_billing, name='settlement_billing'),

    # Settings - Center
    path('settings/centers/', views.CenterListView.as_view(), name='center_list'),
    path('settings/centers/new/', views.CenterCreateView.as_view(), name='center_create'),
    path('settings/centers/<int:pk>/edit/', views.CenterUpdateView.as_view(), name='center_update'),
    path('settings/centers/<int:pk>/delete/', views.CenterDeleteView.as_view(), name='center_delete'),

    # Settings - Shipper
    path('settings/shippers/', views.ShipperListView.as_view(), name='shipper_list'),
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