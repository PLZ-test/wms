# management/apps.py
from django.apps import AppConfig

class ManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'management'
    verbose_name = '기준정보 관리' # 관리자 페이지에 표시될 이름