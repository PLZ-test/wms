from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Center, Shipper, Courier, Product, StockMovement, Order

class CustomUserAdmin(UserAdmin):
    # 기존 UserAdmin의 fieldsets를 복사하고, 마지막에 커스텀 필드셋을 추가합니다.
    fieldsets = UserAdmin.fieldsets + (
        ('역할 및 소속 정보', {'fields': ('role', 'center', 'shipper')}),
    )
    # 기존 UserAdmin의 add_fieldsets를 복사하고, 커스텀 필드를 추가합니다.
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('역할 및 소속 정보', {'fields': ('role', 'center', 'shipper')}),
    )
    # 리스트 화면에 보여줄 필드를 설정합니다.
    list_display = ('username', 'email', 'role', 'center', 'shipper', 'is_staff')
    # 필터 옵션을 추가합니다.
    list_filter = ('role', 'center', 'shipper', 'is_staff', 'is_superuser', 'groups')
    # 검색 필드를 설정합니다.
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

# Django Admin에 모델을 등록합니다.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Center)
admin.site.register(Shipper)
admin.site.register(Courier)
admin.site.register(Product)
admin.site.register(StockMovement)
admin.site.register(Order)