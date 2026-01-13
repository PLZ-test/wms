# orders/api_clients/coupang.py
from .base import BaseApiClient
from typing import List, Dict, Any
from datetime import datetime, timedelta
from django.utils import timezone
import random
import uuid


class CoupangClient(BaseApiClient):
    """쿠팡 API 클라이언트 (Mock 구현)"""
    
    def fetch_orders(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        쿠팡 주문 조회 (Mock 데이터 반환)
        
        실제 구현 시:
        - Vendor ID, Access Key, Secret Key로 인증
        - GET /v2/providers/wing_api/apis/api/v4/vendors/{vendorId}/ordersheets 호출
        """
        # Mock 데이터 생성
        mock_orders = []
        num_orders = random.randint(1, 3)  # 1-3개의 임의 주문 생성
        
        # 현재 시간대(한국 시간) 기준으로 오늘 날짜 사용
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(num_orders):
            # 오늘 00:00 ~ 23:59 사이의 임의 시간
            order_datetime = today_start + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            # UUID를 사용하여 완전히 고유한 주문번호 생성
            unique_suffix = str(uuid.uuid4())[:8]  # UUID의 처음 8자리
            mock_orders.append({
                'order_no': f'CPG-{order_datetime.strftime("%Y%m%d")}-{unique_suffix}',
                'order_date': order_datetime,
                'recipient_name': f'테스트수취인{i+1}',
                'recipient_phone': f'010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                'address': f'서울시 강남구 테헤란로 {random.randint(1, 500)}',
                'postcode': f'{random.randint(10000, 99999)}',
                'delivery_memo': '부재 시 문앞',
                'items': [
                    {
                        'product_identifier': f'PRD-{random.randint(1000, 9999)}',
                        'quantity': random.randint(1, 3),
                    }
                ]
            })
        
        print(f"🔹 쿠팡 Mock API: {num_orders}건의 주문 생성 (오늘 날짜: {now.date()})")
        return mock_orders
