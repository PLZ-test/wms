# core/admin.py

from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

# [추가] 각 앱에서 관리자 페이지에 등록할 모델들을 모두 가져옵니다.
from users.models import User
from users.admin import CustomUserAdmin # users 앱에 정의된 CustomUserAdmin 설정을 가져옵니다.
from management.models import Center, Shipper, Courier, Product, SalesChannel
from stock.models import StockMovement
from orders.models import Order, OrderItem
from orders.admin import OrderAdmin # orders 앱에 정의된 OrderAdmin 설정을 가져옵니다.

class WMSAdminSite(admin.AdminSite):
    """
    # WMS 전용 커스텀 관리자 사이트 클래스
    # 기본 Django 관리자 사이트를 상속받아 필요한 기능을 추가하거나 수정합니다.
    """
    def get_urls(self):
        # 기본 URL 목록을 가져온 후, 커스텀 로그아웃 URL을 맨 앞에 추가합니다.
        urls = super().get_urls()
        # 관리자 페이지에서 로그아웃 시, 관리자 로그인 페이지로 리디렉션되도록 설정합니다.
        urls.insert(0, path('logout/', auth_views.LogoutView.as_view(next_page='admin:login'), name='logout'))
        return urls

# [수정] wms_admin_site 인스턴스를 생성하여 프로젝트 전체에서 사용합니다.
wms_admin_site = WMSAdminSite(name='wms_admin')

# [수정] 모든 모델을 기본 admin.site가 아닌 wms_admin_site에 등록합니다.
# 이렇게 해야 커스텀 관리자 페이지에서 모델들을 관리할 수 있습니다.

# Users 앱 모델 등록
wms_admin_site.register(User, CustomUserAdmin)

# Management 앱 모델 등록
wms_admin_site.register(Center)
wms_admin_site.register(Shipper)
wms_admin_site.register(Courier)
wms_admin_site.register(Product)
wms_admin_site.register(SalesChannel)

# Stock 앱 모델 등록
wms_admin_site.register(StockMovement)

# Orders 앱 모델 등록
# Order 모델은 OrderItem을 함께 볼 수 있도록 OrderAdmin 설정을 적용합니다.
wms_admin_site.register(Order, OrderAdmin)