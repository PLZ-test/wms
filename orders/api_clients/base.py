# orders/api_clients/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class BaseApiClient(ABC):
    """
    모든 쇼핑몰 API 클라이언트의 기본 추상 클래스
    """
    
    def __init__(self, access_key: str, secret_key: str, extra_info: Dict[str, Any] = None):
        """
        Args:
            access_key: API Access Key / Client ID
            secret_key: API Secret Key / Client Secret
            extra_info: 추가 인증 정보 (Vendor ID 등)
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.extra_info = extra_info or {}
    
    @abstractmethod
    def fetch_orders(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        지정된 기간의 주문을 조회합니다.
        
        Args:
            start_date: 조회 시작 시간
            end_date: 조회 종료 시간
        
        Returns:
            주문 목록 (각 주문은 딕셔너리 형태)
            예시:
            [
                {
                    'order_no': '주문번호',
                    'order_date': datetime,
                    'recipient_name': '수취인명',
                    'recipient_phone': '연락처',
                    'address': '주소',
                    'postcode': '우편번호',
                    'delivery_memo': '배송메모',
                    'items': [
                        {
                            'product_identifier': '상품코드 또는 이름',
                            'quantity': 1,
                        }
                    ]
                }
            ]
        """
        pass
    
    def validate_credentials(self) -> bool:
        """
        API 인증 정보가 유효한지 검증합니다.
        
        Returns:
            인증 정보가 유효하면 True, 그렇지 않으면 False
        """
        # 기본 구현: 키가 있는지만 확인
        return bool(self.access_key and self.secret_key)
