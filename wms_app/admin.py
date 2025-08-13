from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Center, Shipper, Courier, Product, StockMovement, Order

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

admin.site.register(User, CustomUserAdmin)
admin.site.register(Center)
admin.site.register(Shipper)
admin.site.register(Courier)
admin.site.register(Product)
admin.site.register(StockMovement)
admin.site.register(Order)