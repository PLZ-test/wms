# settlement/apps.py
from django.apps import AppConfig

class SettlementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settlement'
    verbose_name = '정산 관리' # 관리자 페이지에 표시될 이름