# users/urls.py
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # 인증 URL
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.wms_logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/done/', views.signup_done_view, name='signup_done'),

    # 비밀번호 재설정 URL
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             success_url=reverse_lazy('users:password_reset_done')
         ), 
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url=reverse_lazy('users:password_reset_complete')
         ), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),

    # 사용자 관리 URL
    path('manage/', views.user_manage_view, name='manage'),
    path('manage/<int:pk>/update/', views.user_update_view, name='update'),

    # API URL
    path('api/check-username/', views.check_username_api, name='check_username_api'),
]