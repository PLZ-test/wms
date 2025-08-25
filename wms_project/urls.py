# wms_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from wms_app.admin import wms_admin_site
from wms_app import views as wms_views

# --- 정적 파일 설정을 위해 아래 두 줄이 꼭 필요합니다 ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin 로그아웃 시 admin 로그인 페이지로만 리디렉션되도록 명시적으로 설정
    path('admin/logout/', auth_views.LogoutView.as_view(next_page='admin:login'), name='admin_logout'),
    # Django 기본 admin.site.urls 대신 wms_admin_site.urls를 사용합니다.
    path('admin/', wms_admin_site.urls),

    # --- WMS 앱의 인증 관련 URL ---
    path('login/', wms_views.CustomLoginView.as_view(), name='login'),
    path('logout/', wms_views.wms_logout_view, name='logout'),
    path('signup/', wms_views.signup_view, name='signup'),
    path('signup/done/', wms_views.signup_done_view, name='signup_done'),

    # --- [추가] 비밀번호 재설정 관련 URL ---
    # 1. 비밀번호 재설정 요청 (이메일 입력) - name='password_reset'
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), 
         name='password_reset'),
    
    # 2. 이메일 발송 완료 안내
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),
    
    # 3. 이메일 링크 클릭 후 비밀번호 재설정
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    
    # 4. 비밀번호 재설정 완료
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'),
    # -----------------------------------------

    path('', include('wms_app.urls')),
]

# --- 개발 모드(DEBUG=True)일 때만 static 파일 경로를 추가하는 코드 ---
# 이 부분이 없으면 runserver에서 CSS 파일을 찾지 못합니다.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])