# stock/admin.py
from django.contrib import admin
from .models import StockMovement

# wms_admin_site에 등록하기 위해 주석 처리 (프로젝트 admin.py에서 직접 등록)
# admin.site.register(StockMovement)