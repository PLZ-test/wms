# stock/models.py
from django.db import models
from management.models import Center

# [삭제] 기존 WarehouseLayout 모델은 더 이상 사용하지 않으므로 삭제합니다.

class Location(models.Model):
    """
    # [변경] 창고 내 재고 위치(구역) 정보를 담는 모델
    # 기존: 도면 좌표 기반 -> 변경: 구역, 위치명, 최대 층수 기반
    """
    # 소속 센터: 어떤 물류센터에 속한 위치인지를 나타냅니다.
    center = models.ForeignKey(Center, on_delete=models.CASCADE, verbose_name='소속 센터')
    # 구역명: A구역, B구역 등 큰 단위의 구역을 지정합니다.
    zone = models.CharField(max_length=50, verbose_name='구역명 (예: A구역)')
    # 위치명: A-01, B-01 등 구역 내에서의 고유한 위치 이름을 지정합니다.
    name = models.CharField(max_length=100, verbose_name='위치명 (예: A-01)')
    # 최대 층수: 해당 위치가 몇 개의 층으로 이루어져 있는지 숫자로 정의합니다.
    max_floor = models.PositiveIntegerField(default=1, verbose_name='최대 층수')
    description = models.TextField(blank=True, verbose_name='설명')

    class Meta:
        verbose_name = '재고 위치'
        verbose_name_plural = '재고 위치'
        # [추가] 한 센터 내에서는 동일한 구역과 위치명을 중복해서 사용할 수 없도록 제약조건을 추가합니다.
        unique_together = ('center', 'zone', 'name')

    def __str__(self):
        return f'[{self.center.name}] {self.zone} / {self.name}'


class StockMovement(models.Model):
    """
    상품의 재고 입출고 내역을 기록하는 모델 (기존 구조 유지)
    """
    MOVEMENT_TYPES = [
        ('IN', '입고'),
        ('OUT', '출고')
    ]
    BOX_SIZE_CHOICES = [
        ('S', '소형'),
        ('M', '중형'),
        ('L', '대형'),
        ('XL', '특대형'),
    ]

    product = models.ForeignKey('management.Product', on_delete=models.CASCADE, verbose_name='상품')
    # [변경] location 필드의 ForeignKey가 새로운 Location 모델을 가리키도록 자동으로 연결됩니다.
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='위치')
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES, verbose_name='구분')
    quantity = models.PositiveIntegerField(verbose_name='수량')
    memo = models.TextField(blank=True, verbose_name='메모')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='일시')
    
    # 층, 박스 크기 필드는 그대로 유지하여 입고 시 상세 정보를 기록하는 데 사용합니다.
    floor = models.PositiveIntegerField(default=1, verbose_name='층')
    box_size = models.CharField(max_length=10, choices=BOX_SIZE_CHOICES, null=True, blank=True, verbose_name='박스 크기')

    class Meta:
        verbose_name = '재고 이동 기록'
        verbose_name_plural = '재고 이동 기록'
        
    def __str__(self):
        return f'[{self.get_movement_type_display()}] {self.product.name} - {self.quantity}개 ({self.timestamp})'