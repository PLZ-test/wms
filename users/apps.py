# users/apps.py
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # 이 name이 settings.py의 'users'와 일치해야 합니다.
    name = 'users'
    verbose_name = '사용자 관리'