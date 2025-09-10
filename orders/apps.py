# orders/apps.py

from django.apps import AppConfig

# [신규] orders 앱의 설정을 담당하는 클래스입니다.
# 클래스 이름은 settings.py의 INSTALLED_APPS에 명시된 'OrdersConfig'와 정확히 일치해야 합니다.
class OrdersConfig(AppConfig):
    """
    orders 앱의 설정 클래스
    """
    # Django가 모델의 기본 키(Primary Key)를 자동으로 생성할 때 사용할 필드 타입입니다.
    default_auto_field = 'django.db.models.BigAutoField'
    
    # 이 앱의 고유한 이름입니다.
    name = 'orders'
    
    # 관리자 페이지 등에서 보여줄 앱의 한글 이름입니다.
    verbose_name = '주문 관리'