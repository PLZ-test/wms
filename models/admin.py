# management/admin.py
from django.contrib import admin
from .models import Center, Shipper, Courier, Product, SalesChannel

# wms_admin_site에 등록하기 위해 주석 처리 (프로젝트 admin.py에서 직접 등록)
# admin.site.register(Center)
# admin.site.register(Shipper)
# admin.site.register(Courier)
# admin.site.register(Product)
# admin.site.register(SalesChannel)