# core/admin.py
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from users.models import User
from users.admin import CustomUserAdmin
from management.models import Center, Shipper, Courier, Product, SalesChannel
# [수정] stock.models에서 더 이상 사용하지 않는 WarehouseLayout를 import 목록에서 삭제합니다.
from stock.models import StockMovement, Location
from orders.models import Order, OrderItem
from orders.admin import OrderAdmin

class WMSAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        urls.insert(0, path('logout/', auth_views.LogoutView.as_view(next_page='admin:login'), name='logout'))
        return urls

wms_admin_site = WMSAdminSite(name='wms_admin')

# ... (다른 모델 등록은 동일) ...
wms_admin_site.register(User, CustomUserAdmin)
wms_admin_site.register(Center)
wms_admin_site.register(Shipper)
wms_admin_site.register(Courier)
wms_admin_site.register(Product)
wms_admin_site.register(SalesChannel)
wms_admin_site.register(Order, OrderAdmin)

# Stock 앱 모델들을 등록합니다.
wms_admin_site.register(StockMovement)
wms_admin_site.register(Location) 
# [삭제] WarehouseLayout 등록 코드를 삭제합니다.