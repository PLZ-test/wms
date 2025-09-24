# stock/admin.py
from django.contrib import admin
from .models import WarehouseLayout, Location, StockMovement

# [수정] wms_admin_site 인스턴스에 직접 등록하도록 변경
# from core.admin import wms_admin_site # 이 라인은 더 이상 필요 없습니다.

class WarehouseLayoutAdmin(admin.ModelAdmin):
    """
    WarehouseLayout 모델을 위한 커스텀 관리자 페이지 설정
    """
    # 기본 change_form 템플릿 대신 우리가 만들 커스텀 템플릿을 사용하도록 지정
    change_form_template = 'admin/stock/warehouse_layout_change_form.html'

# 이 파일에서는 더 이상 admin.site.register나 wms_admin_site.register를 사용하지 않습니다.
# 모든 모델 등록은 core/admin.py에서 중앙 관리합니다.