# management/models.py
from django.db import models

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
    contact = models.CharField(max_length=100, blank=True, verbose_name='담당자')
    
    class Meta:
        verbose_name = '화주사'
        verbose_name_plural = '화주사'
        
    def __str__(self):
        return self.name

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
    shipper = models.ForeignKey(Shipper, on_delete=models.CASCADE, verbose_name='화주사')
    name = models.CharField(max_length=200, verbose_name='상품명')
    barcode = models.CharField(max_length=100, unique=True, verbose_name='바코드')
    width = models.FloatField(default=0, verbose_name='가로(cm)')
    length = models.FloatField(default=0, verbose_name='세로(cm)')
    height = models.FloatField(default=0, verbose_name='높이(cm)')
    quantity = models.PositiveIntegerField(default=0, verbose_name='재고 수량') # 이 필드는 stock 앱에서 관리될 예정
    
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