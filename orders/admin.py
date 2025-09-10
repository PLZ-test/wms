# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    """
    Order 상세 페이지에서 OrderItem을 함께 관리하기 위한 인라인 설정
    """
    model = OrderItem
    extra = 1  # 기본으로 보여줄 빈 아이템 폼의 수

class OrderAdmin(admin.ModelAdmin):
    """
    관리자 페이지에서 Order 모델을 커스터마이징하기 위한 설정
    """
    inlines = [OrderItemInline] # Order 상세 페이지에 OrderItem 인라인을 포함
    list_display = ('order_no', 'shipper', 'channel', 'recipient_name', 'order_status', 'created_at')
    list_filter = ('order_status', 'shipper', 'channel')
    search_fields = ('order_no', 'recipient_name')

# wms_admin_site에 등록하기 위해 주석 처리 (프로젝트 admin.py에서 직접 등록)
# admin.site.register(Order, OrderAdmin)