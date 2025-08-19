from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from wms_app.admin import wms_admin_site
from wms_app import views as wms_views # wms_views를 import 합니다.

# --- 정적 파일 설정을 위해 아래 두 줄이 꼭 필요합니다 ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin 로그아웃 시 admin 로그인 페이지로만 리디렉션되도록 명시적으로 설정
    path('admin/logout/', auth_views.LogoutView.as_view(next_page='admin:login'), name='admin_logout'),
    # Django 기본 admin.site.urls 대신 wms_admin_site.urls를 사용합니다.
    path('admin/', wms_admin_site.urls),

    # --- [추가] WMS 앱의 인증 관련 URL을 최상위로 옮겼습니다. ---
    path('login/', wms_views.CustomLoginView.as_view(), name='login'),
    path('logout/', wms_views.wms_logout_view, name='logout'),
    path('signup/', wms_views.signup_view, name='signup'),
    path('signup/done/', wms_views.signup_done_view, name='signup_done'),

    path('', include('wms_app.urls')),
]

# --- 개발 모드(DEBUG=True)일 때만 static 파일 경로를 추가하는 코드 ---
# 이 부분이 없으면 runserver에서 CSS 파일을 찾지 못합니다.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])