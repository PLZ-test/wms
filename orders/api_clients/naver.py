# orders/api_clients/naver.py
from .base import BaseApiClient
from typing import List, Dict, Any
from datetime import datetime, timedelta
from django.utils import timezone
import random
import uuid


class NaverClient(BaseApiClient):
    """네이버 스마트스토어 API 클라이언트 (Mock 구현)"""
    
    def fetch_orders(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """네이버 스마트스토어 주문 조회 (Mock 데이터 반환)"""
        mock_orders = []
        num_orders = random.randint(0, 2)
        
        # 현재 시간대 기준 오늘 날짜
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(num_orders):
            order_datetime = today_start + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            unique_suffix = str(uuid.uuid4())[:8]
            
            mock_orders.append({
                'order_no': f'NAVER-{order_datetime.strftime("%Y%m%d")}-{unique_suffix}',
                'order_date': order_datetime,
                'recipient_name': f'네이버고객{i+1}',
                'recipient_phone': f'010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                'address': f'경기도 성남시 분당구 판교역로 {random.randint(1, 200)}',
                'postcode': f'{random.randint(10000, 99999)}',
                'delivery_memo': '배송 전 연락 요망',
                'items': [
                    {
                        'product_identifier': f'NAVER-PRD-{random.randint(1000, 9999)}',
                        'quantity': random.randint(1, 2),
                    }
                ]
            })
        
        print(f"🔹 네이버 Mock API: {num_orders}건의 주문 생성 (오늘 날짜: {now.date()})")
        return mock_orders
