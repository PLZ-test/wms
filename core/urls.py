# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # 대시보드 URL: 웹사이트의 루트 경로('')에 해당합니다.
    path('', views.dashboard, name='dashboard'),
]