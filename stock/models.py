# stock/models.py
from django.db import models
from management.models import Center

class WarehouseLayout(models.Model):
    """
    센터별 창고 도면 정보를 담는 모델
    """
    center = models.OneToOneField(Center, on_delete=models.CASCADE, verbose_name='소속 센터')
    name = models.CharField(max_length=100, verbose_name='도면명 (예: 1층 A구역)')
    image = models.ImageField(upload_to='layouts/', verbose_name='도면 이미지')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='업로드 일시')

    class Meta:
        verbose_name = '창고 도면'
        verbose_name_plural = '창고 도면'

    def __str__(self):
        return f'[{self.center.name}] {self.name}'


class Location(models.Model):
    """
    창고 내 재고 위치 정보를 담는 모델 (좌표 정보 포함)
    """
    layout = models.ForeignKey(WarehouseLayout, on_delete=models.CASCADE, verbose_name='소속 도면', null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name='위치명 (예: A-1-1)')
    description = models.TextField(blank=True, verbose_name='설명')
    
    x_coord = models.FloatField(verbose_name='X 좌표 (%)', default=0)
    y_coord = models.FloatField(verbose_name='Y 좌표 (%)', default=0)
    width = models.FloatField(verbose_name='너비 (%)', default=0)
    height = models.FloatField(verbose_name='높이 (%)', default=0)

    class Meta:
        verbose_name = '재고 위치'
        verbose_name_plural = '재고 위치'

    def __str__(self):
        center_name = self.layout.center.name if self.layout else "미지정"
        return f'[{center_name}] {self.name}'


class StockMovement(models.Model):
    """
    상품의 재고 입출고 내역을 기록하는 모델
    """
    MOVEMENT_TYPES = [
        ('IN', '입고'),
        ('OUT', '출고')
    ]
    # [추가] 박스 크기 선택지를 정의합니다.
    BOX_SIZE_CHOICES = [
        ('S', '소형'),
        ('M', '중형'),
        ('L', '대형'),
        ('XL', '특대형'),
    ]

    product = models.ForeignKey('management.Product', on_delete=models.CASCADE, verbose_name='상품')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='위치')
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES, verbose_name='구분')
    quantity = models.PositiveIntegerField(verbose_name='수량')
    memo = models.TextField(blank=True, verbose_name='메모')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='일시')
    
    # [신규] 층, 박스 크기 필드를 추가합니다.
    floor = models.PositiveIntegerField(default=1, verbose_name='층')
    box_size = models.CharField(max_length=10, choices=BOX_SIZE_CHOICES, null=True, blank=True, verbose_name='박스 크기')

    class Meta:
        verbose_name = '재고 이동 기록'
        verbose_name_plural = '재고 이동 기록'
        
    def __str__(self):
        return f'[{self.get_movement_type_display()}] {self.product.name} - {self.quantity}개 ({self.timestamp})'