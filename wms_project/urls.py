# wms_project/urls.py
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# core/admin.py 파일에서 wms_admin_site 인스턴스를 가져옵니다.
# from core.admin import wms_admin_site # <--- 주석 처리

urlpatterns = [
    # 관리자 페이지 URL은 이제 core.admin에 정의된 wms_admin_site를 사용합니다.
    # path('admin/', wms_admin_site.urls), # <--- 주석 처리
    # ...
]

    # 각 앱의 urls.py 파일을 포함(include)합니다.
    path('users/', include('users.urls', namespace='users')),
    path('management/', include('management.urls', namespace='management')),
    path('stock/', include('stock.urls', namespace='stock')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('settlement/', include('settlement.urls', namespace='settlement')),

    # 루트 URL 경로는 core 앱이 담당합니다.
    path('', include('core.urls', namespace='core')),
]

# 개발 환경에서 static 파일을 처리하기 위한 설정
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])