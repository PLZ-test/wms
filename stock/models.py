# stock/models.py
from django.db import models

class StockMovement(models.Model):
    """
    상품의 재고 입출고 내역을 기록하는 모델
    """
    MOVEMENT_TYPES = [
        ('IN', '입고'),
        ('OUT', '출고')
    ]
    # management 앱의 Product 모델과 관계를 맺습니다.
    product = models.ForeignKey('management.Product', on_delete=models.CASCADE, verbose_name='상품')
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES, verbose_name='구분')
    quantity = models.PositiveIntegerField(verbose_name='수량')
    memo = models.TextField(blank=True, verbose_name='메모')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='일시')
    
    class Meta:
        verbose_name = '재고 이동 기록'
        verbose_name_plural = '재고 이동 기록'
        
    def __str__(self):
        return f'[{self.get_movement_type_display()}] {self.product.name} - {self.quantity}개 ({self.timestamp})'