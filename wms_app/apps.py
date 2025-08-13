from django.apps import AppConfig

class WmsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wms_app'
    verbose_name = 'WMS 관리'  # 관리자 페이지에 표시될 앱의 한글 이름