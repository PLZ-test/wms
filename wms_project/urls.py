# wms_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# [수정] core.admin 파일에서 wms_admin_site 인스턴스를 가져옵니다.
# 이 코드는 커스텀 관리자 페이지를 사용하기 위해 필수적입니다.
from core.admin import wms_admin_site

urlpatterns = [
    # [수정] Django 기본 admin.site.urls 대신 우리가 만든 wms_admin_site.urls를 사용하도록 경로를 수정합니다.
    path('admin/', wms_admin_site.urls),

    # 각 앱의 urls.py 파일을 포함(include)하여 URL을 분리 관리합니다.
    # 각 앱의 기능별로 URL을 그룹화하여 유지보수성을 높입니다.
    path('users/', include('users.urls', namespace='users')),
    path('management/', include('management.urls', namespace='management')),
    path('stock/', include('stock.urls', namespace='stock')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('settlement/', include('settlement.urls', namespace='settlement')),

    # [수정] 루트 URL('') 경로는 이제 core 앱의 urls.py에서 처리합니다.
    # 사용자가 웹사이트의 메인 주소로 접속했을 때 core 앱의 대시보드가 보이게 됩니다.
    path('', include('core.urls', namespace='core')),
]

# [수정] 개발 환경(DEBUG=True)에서 static 및 media 파일을 올바르게 처리하기 위한 설정입니다.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    # [추가] 사용자가 업로드한 미디어 파일(예: 도면 이미지)을 서빙하기 위한 URL 패턴
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)