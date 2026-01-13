# orders/api_clients/elevenst.py
from .base import BaseApiClient
from typing import List, Dict, Any
from datetime import datetime, timedelta
from django.utils import timezone
import random
import uuid


class ElevenSTClient(BaseApiClient):
    """11번가 API 클라이언트 (Mock 구현)"""
    
    def fetch_orders(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        mock_orders = []
        num_orders = random.randint(0, 2)
        
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(num_orders):
            order_datetime = today_start + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            unique_suffix = str(uuid.uuid4())[:8]
            
            mock_orders.append({
                'order_no': f'11ST-{order_datetime.strftime("%Y%m%d")}-{unique_suffix}',
                'order_date': order_datetime,
                'recipient_name': f'11번가고객{i+1}',
                'recipient_phone': f'010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                'address': f'서울시 영등포구 여의도동 {random.randint(1, 100)}',
                'postcode': f'{random.randint(10000, 99999)}',
                'delivery_memo': '',
                'items': [
                    {
                        'product_identifier': f'11ST-PRD-{random.randint(1000, 9999)}',
                        'quantity': 1,
                    }
                ]
            })
        
        print(f"🔹 11번가 Mock API: {num_orders}건의 주문 생성 (오늘 날짜: {now.date()})")
        return mock_orders
