# management/models.py
from django.db import models
# [삭제] 순환 참조의 원인이 되는 import 구문을 삭제합니다.
# from stock.models import StockMovement

class Center(models.Model):
    """
    물류 센터 정보를 담는 모델
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='센터명')
    address = models.CharField(max_length=255, verbose_name='주소')
    
    class Meta:
        verbose_name = '센터'
        verbose_name_plural = '센터'

    def __str__(self):
        return self.name

class Shipper(models.Model):
    """
    화주사 정보를 담는 모델
    """
    center = models.ForeignKey(Center, on_delete=models.CASCADE, verbose_name='소속 센터')
    name = models.CharField(max_length=100, unique=True, verbose_name='화주사명')
    contact = models.CharField(max_length=100, blank=True, null=True, verbose_name='연락처')
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name='주소')
    
    class Meta:
        verbose_name = '화주사'
        verbose_name_plural = '화주사'
        
    def __str__(self):
        return self.name

class ShipperApiInfo(models.Model):
    CHANNEL_CHOICES = [
        ('COUPANG', '쿠팡 (Coupang)'),
        ('NAVER', '네이버 스마트스토어 (Naver SmartStore)'),
        ('11ST', '11번가 (11st)'),
        ('GMARKET', 'G마켓 (Gmarket)'),
        ('AUCTION', '옥션 (Auction)'),
        ('WEMAKEPRICE', '위메프 (WeMakePrice)'),
        ('TMON', '티몬 (TMON)'),
        ('INTERPARK', '인터파크 (Interpark)'),
    ]
    
    shipper = models.ForeignKey(Shipper, on_delete=models.CASCADE, related_name='api_infos', verbose_name='화주사')
    channel_type = models.CharField(max_length=20, choices=CHANNEL_CHOICES, verbose_name='쇼핑몰')
    
    # 공통 인증 정보
    access_key = models.CharField(max_length=255, verbose_name='Access Key / Client ID')
    secret_key = models.CharField(max_length=255, verbose_name='Secret Key / Client Secret')
    
    # 추가 정보 (Vendor ID 등 딕셔너리 형태 저장)
    extra_info = models.TextField(blank=True, default='{}', verbose_name='추가 정보(JSON)')
    
    is_active = models.BooleanField(default=True, verbose_name='활성화 여부')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '화주사 API 정보'
        verbose_name_plural = '화주사 API 정보 목록'
        unique_together = ('shipper', 'channel_type')

    def __str__(self):
        return f"{self.shipper.name} - {self.get_channel_type_display()}"


class Courier(models.Model):
    """
    택배사 정보를 담는 모델
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='택배사명')
    contact = models.CharField(max_length=100, blank=True, verbose_name='연락처')
    
    class Meta:
        verbose_name = '택배사'
        verbose_name_plural = '택배사'
        
    def __str__(self):
        return self.name

class Product(models.Model):
    """
    상품 정보를 담는 모델
    """
    # --- [신규] '박스 크기' 선택지를 모델 내에 직접 정의합니다. ---
    BOX_SIZE_CHOICES = [
        ('S', '소형'),
        ('M', '중형'),
        ('L', '대형'),
        ('XL', '특대형'),
    ]

    shipper = models.ForeignKey(Shipper, on_delete=models.CASCADE, verbose_name='화주사')
    name = models.CharField(max_length=200, verbose_name='상품명')
    barcode = models.CharField(max_length=100, unique=True, verbose_name='바코드')
    width = models.FloatField(default=0, verbose_name='가로(cm)')
    length = models.FloatField(default=0, verbose_name='세로(cm)')
    height = models.FloatField(default=0, verbose_name='높이(cm)')
    quantity = models.PositiveIntegerField(default=0, verbose_name='재고 수량')
    
    products_per_pallet = models.PositiveIntegerField(default=0, verbose_name='파렛트 당 상품 수')
    pallet_quantity = models.PositiveIntegerField(default=0, verbose_name='파렛트 수량')

    # '박스 크기' 필드가 위에서 정의한 선택지를 사용하도록 수정합니다.
    box_size = models.CharField(
        max_length=10, 
        choices=BOX_SIZE_CHOICES, 
        default='S',
        verbose_name='박스 크기'
    )
    
    class Meta:
        verbose_name = '상품'
        verbose_name_plural = '상품'
        
    def __str__(self):
        return f'[{self.shipper.name}] {self.name}'

class SalesChannel(models.Model):
    """
    판매 채널 정보를 담는 모델 (예: 쿠팡, 스마트스토어 등)
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='판매 채널명')
    
    class Meta:
        verbose_name = '판매 채널'
        verbose_name_plural = '판매 채널'
        
    def __str__(self):
        return self.name