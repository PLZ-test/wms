from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # ✅ 추가

# --- 정적 파일 설정을 위해 아래 두 줄이 꼭 필요합니다 ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('wms_app.urls')),

    # ✅ 로그인/로그아웃 URL 추가
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
]

# --- 개발 모드(DEBUG=True)일 때만 static 파일 경로를 추가하는 코드 ---
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
