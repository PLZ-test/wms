# management/urls.py
from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    # 대시보드
    path('dashboard/', views.management_dashboard, name='dashboard'),

    # Center (센터)
    path('centers/', views.CenterListView.as_view(), name='center_list'),
    path('centers/new/', views.CenterCreateView.as_view(), name='center_create'),
    path('centers/<int:pk>/edit/', views.CenterUpdateView.as_view(), name='center_update'),
    path('centers/<int:pk>/delete/', views.CenterDeleteView.as_view(), name='center_delete'),

    # Shipper (화주사)
    path('shippers/', views.ShipperListView.as_view(), name='shipper_list'),
    path('shippers/new/', views.ShipperCreateView.as_view(), name='shipper_create'),
    path('shippers/<int:pk>/edit/', views.ShipperUpdateView.as_view(), name='shipper_update'),
    path('shippers/<int:pk>/delete/', views.ShipperDeleteView.as_view(), name='shipper_delete'),

    # Courier (택배사)
    path('couriers/', views.CourierListView.as_view(), name='courier_list'),
    path('couriers/new/', views.CourierCreateView.as_view(), name='courier_create'),
    path('couriers/<int:pk>/edit/', views.CourierUpdateView.as_view(), name='courier_update'),
    path('couriers/<int:pk>/delete/', views.CourierDeleteView.as_view(), name='courier_delete'),

    # Product (상품)
    path('shippers/<int:shipper_pk>/products/', views.product_list_view, name='product_list'),
    path('shippers/<int:shipper_pk>/products/new/', views.product_create_view, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update_view, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete_view, name='product_delete'),
    
    # --- [추가] 대시보드에서 직접 상품을 등록하는 URL ---
    path('products/new-direct/', views.product_create_direct_view, name='product_create_direct'),
]