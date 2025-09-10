# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    """
    관리자 페이지의 사용자 모델 표시를 커스터마이징합니다.
    """
    # 사용자 정보 수정 화면에 '역할 및 소속 정보' 섹션 추가
    fieldsets = UserAdmin.fieldsets + (
        ('역할 및 소속 정보', {'fields': ('role', 'center', 'shipper')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('역할 및 소속 정보', {'fields': ('role', 'center', 'shipper')}),
    )
    # 사용자 목록에 보여줄 필드 지정
    list_display = ('username', 'email', 'role', 'center', 'shipper', 'is_staff', 'is_active')
    # 필터 옵션 추가
    list_filter = ('role', 'is_active', 'center', 'shipper', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

# admin.site.register(User, CustomUserAdmin) # 이 줄은 주석 처리된 상태로 둡니다.