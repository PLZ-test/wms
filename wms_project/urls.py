from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('wms_app.urls')), # 앱의 urls.py를 메인 URLConf에 연결합니다.
]