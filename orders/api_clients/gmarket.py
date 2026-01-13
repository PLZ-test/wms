# orders/api_clients/gmarket.py
from .base import BaseApiClient
from typing import List, Dict, Any
from datetime import datetime, timedelta
from django.utils import timezone
import random
import uuid


class GmarketClient(BaseApiClient):
    """G마켓 API 클라이언트 (Mock 구현)"""
    
    def fetch_orders(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        mock_orders = []
        num_orders = random.randint(0, 1)  # 0-1개
        
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(num_orders):
            order_datetime = today_start + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            unique_suffix = str(uuid.uuid4())[:8]
            
            mock_orders.append({
                'order_no': f'GMARKET-{order_datetime.strftime("%Y%m%d")}-{unique_suffix}',
                'order_date': order_datetime,
                'recipient_name': f'G마켓고객{i+1}',
                'recipient_phone': f'010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                'address': f'서울시 강남구 역삼동 {random.randint(1, 300)}',
                'postcode': f'{random.randint(10000, 99999)}',
                'delivery_memo': '문앞에 놓아주세요',
                'items': [
                    {
                        'product_identifier': f'GM-PRD-{random.randint(1000, 9999)}',
                        'quantity': random.randint(1, 2),
                    }
                ]
            })
        
        print(f"🔹 G마켓 Mock API: {num_orders}건의 주문 생성")
        return mock_orders


class AuctionClient(BaseApiClient):
    """옥션 API 클라이언트 (Mock 구현)"""
    
    def fetch_orders(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        mock_orders = []
        num_orders = random.randint(0, 1)
        
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(num_orders):
            order_datetime = today_start + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            unique_suffix = str(uuid.uuid4())[:8]
            
            mock_orders.append({
                'order_no': f'AUCTION-{order_datetime.strftime("%Y%m%d")}-{unique_suffix}',
                'order_date': order_datetime,
                'recipient_name': f'옥션고객{i+1}',
                'recipient_phone': f'010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                'address': f'부산시 해운대구 우동 {random.randint(1, 200)}',
                'postcode': f'{random.randint(10000, 99999)}',
                'delivery_memo': '',
                'items': [
                    {
                        'product_identifier': f'AUC-PRD-{random.randint(1000, 9999)}',
                        'quantity': 1,
                    }
                ]
            })
        
        print(f"🔹 옥션 Mock API: {num_orders}건의 주문 생성")
        return mock_orders


class WemakepriceClient(BaseApiClient):
    """위메프 API 클라이언트 (Mock 구현)"""
    
    def fetch_orders(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        mock_orders = []
        num_orders = random.randint(0, 1)
        
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(num_orders):
            order_datetime = today_start + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            unique_suffix = str(uuid.uuid4())[:8]
            
            mock_orders.append({
                'order_no': f'WMP-{order_datetime.strftime("%Y%m%d")}-{unique_suffix}',
                'order_date': order_datetime,
                'recipient_name': f'위메프고객{i+1}',
                'recipient_phone': f'010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                'address': f'인천시 남동구 구월동 {random.randint(1, 150)}',
                'postcode': f'{random.randint(10000, 99999)}',
                'delivery_memo': '경비실',
                'items': [
                    {
                        'product_identifier': f'WMP-PRD-{random.randint(1000, 9999)}',
                        'quantity': 1,
                    }
                ]
            })
        
        print(f"🔹 위메프 Mock API: {num_orders}건의 주문 생성")
        return mock_orders


class TmonClient(BaseApiClient):
    """티몬 API 클라이언트 (Mock 구현)"""
    
    def fetch_orders(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        mock_orders = []
        num_orders = random.randint(0, 1)
        
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(num_orders):
            order_datetime = today_start + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            unique_suffix = str(uuid.uuid4())[:8]
            
            mock_orders.append({
                'order_no': f'TMON-{order_datetime.strftime("%Y%m%d")}-{unique_suffix}',
                'order_date': order_datetime,
                'recipient_name': f'티몬고객{i+1}',
                'recipient_phone': f'010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                'address': f'대전시 유성구 봉명동 {random.randint(1, 100)}',
                'postcode': f'{random.randint(10000, 99999)}',
                'delivery_memo': '배송 전 전화',
                'items': [
                    {
                        'product_identifier': f'TMON-PRD-{random.randint(1000, 9999)}',
                        'quantity': random.randint(1, 2),
                    }
                ]
            })
        
        print(f"🔹 티몬 Mock API: {num_orders}건의 주문 생성")
        return mock_orders


class InterparkClient(BaseApiClient):
    """인터파크 API 클라이언트 (Mock 구현)"""
    
    def fetch_orders(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        mock_orders = []
        num_orders = random.randint(0, 1)
        
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(num_orders):
            order_datetime = today_start + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            unique_suffix = str(uuid.uuid4())[:8]
            
            mock_orders.append({
                'order_no': f'IPARK-{order_datetime.strftime("%Y%m%d")}-{unique_suffix}',
                'order_date': order_datetime,
                'recipient_name': f'인터파크고객{i+1}',
                'recipient_phone': f'010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                'address': f'광주시 서구 치평동 {random.randint(1, 80)}',
                'postcode': f'{random.randint(10000, 99999)}',
                'delivery_memo': '',
                'items': [
                    {
                        'product_identifier': f'IPARK-PRD-{random.randint(1000, 9999)}',
                        'quantity': 1,
                    }
                ]
            })
        
        print(f"🔹 인터파크 Mock API: {num_orders}건의 주문 생성")
        return mock_orders
