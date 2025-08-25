# wms_app/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# --- [수정] SalesChannel과 OrderItem 모델을 import합니다. ---
from .models import User, Center, Shipper, Courier, Product, StockMovement, Order, SalesChannel, OrderItem

from django.urls import path
from django.contrib.auth import views as auth_views

class WMSAdminSite(admin.AdminSite):
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
    list_display = ('username', 'email', 'role', 'center', 'shipper', 'is_staff', 'is_active')
    list_filter = ('role', 'is_active', 'center', 'shipper', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

# --- [신규] OrderAdmin 설정 ---
# OrderItem을 Order 상세 페이지에서 함께 관리할 수 있도록 인라인으로 설정합니다.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # 기본으로 보여줄 빈 아이템 폼의 수

class OrderAdmin(admin.ModelAdmin):
    # Order 상세 페이지에 OrderItem 인라인을 포함시킵니다.
    inlines = [OrderItemInline]
    list_display = ('order_no', 'shipper', 'channel', 'recipient_name', 'order_status', 'created_at')
    list_filter = ('order_status', 'shipper', 'channel')
    search_fields = ('order_no', 'recipient_name')
# -----------------------------

# --- wms_admin_site에 모델을 등록합니다. ---
wms_admin_site.register(User, CustomUserAdmin)
wms_admin_site.register(Center)
wms_admin_site.register(Shipper)
wms_admin_site.register(Courier)
wms_admin_site.register(Product)
wms_admin_site.register(StockMovement)

# --- [수정] Order를 새로운 OrderAdmin과 함께 등록하고, SalesChannel도 등록합니다. ---
wms_admin_site.register(Order, OrderAdmin)
wms_admin_site.register(SalesChannel)
# -------------------------------------------------------------------------