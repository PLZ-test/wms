# stock/apps.py
from django.apps import AppConfig

class StockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stock'
    verbose_name = '재고 관리' # 관리자 페이지에 표시될 이름