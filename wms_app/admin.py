from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Center, Shipper, Courier, Product, StockMovement, Order

# --- [추가] Admin 로그아웃 경로를 분리하기 위한 사용자 정의 AdminSite 클래스 ---
from django.urls import path
from django.contrib.auth import views as auth_views

class WMSAdminSite(admin.AdminSite):
    # 관리자 페이지의 로그아웃 URL을 오버라이딩합니다.
    # 로그아웃 후 'admin:login' 페이지로 리디렉션되게 합니다.
    def get_urls(self):
        urls = super().get_urls()
        urls.insert(0, path('logout/', auth_views.LogoutView.as_view(next_page='admin:login'), name='logout'))
        return urls

wms_admin_site = WMSAdminSite(name='wms_admin')

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('역할 및 소속 정보', {'fields': ('role', 'center', 'shipper')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('역할 및 소속 정보', {'fields': ('role', 'center', 'shipper')}),
    )
    # --- [수정] list_display와 list_filter에 'is_active' 추가 ---
    list_display = ('username', 'email', 'role', 'center', 'shipper', 'is_staff', 'is_active')
    list_filter = ('role', 'is_active', 'center', 'shipper', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

# --- [수정] admin.site 대신 wms_admin_site에 모델을 등록합니다. ---
wms_admin_site.register(User, CustomUserAdmin)
wms_admin_site.register(Center)
wms_admin_site.register(Shipper)
wms_admin_site.register(Courier)
wms_admin_site.register(Product)
wms_admin_site.register(StockMovement)
wms_admin_site.register(Order)