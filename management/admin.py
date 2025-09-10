# management/admin.py
from django.contrib import admin
from .models import Center, Shipper, Courier, Product, SalesChannel

# 이 파일은 비워두거나, 아래처럼 주석 처리합니다.
# 실제 모델 등록은 wms_project/urls.py의 커스텀 AdminSite에서 직접 처리합니다.
# admin.site.register(Center)
# admin.site.register(Shipper)
# admin.site.register(Courier)
# admin.site.register(Product)
# admin.site.register(SalesChannel)