from django.contrib import admin
from django.urls import path, include

# --- 정적 파일 설정을 위해 아래 두 줄이 꼭 필요합니다 ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('wms_app.urls')),
]

# --- 개발 모드(DEBUG=True)일 때만 static 파일 경로를 추가하는 코드 ---
# 이 부분이 없으면 runserver에서 CSS 파일을 찾지 못합니다.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])