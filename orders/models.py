# orders/models.py
from django.db import models
from django.utils import timezone

class Order(models.Model):
    """
    주문 정보를 담는 모델
    """
    ORDER_STATUS_CHOICES = [
        ('PENDING', '주문접수'),
        ('PROCESSING', '처리중'),
        ('SHIPPED', '출고완료'),
        ('DELIVERED', '배송완료'),
        ('CANCELED', '주문취소'),
        ('ERROR', '오류'),
    ]

    # 다른 앱의 모델을 문자열 형태로 참조합니다.
    shipper = models.ForeignKey('management.Shipper', on_delete=models.SET_NULL, null=True, verbose_name='화주사')
    channel = models.ForeignKey('management.SalesChannel', on_delete=models.SET_NULL, null=True, verbose_name='판매 채널')
    
    order_no = models.CharField(max_length=100, verbose_name='주문번호', null=True, blank=True)
    order_date = models.DateTimeField(verbose_name='주문일시')
    recipient_name = models.CharField(max_length=100, verbose_name='수취인명', blank=True)
    recipient_phone = models.CharField(max_length=20, verbose_name='연락처', blank=True)
    address = models.CharField(max_length=255, verbose_name='주소', blank=True)
    postcode = models.CharField(max_length=10, verbose_name='우편번호', blank=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING', verbose_name='주문 상태')
    delivery_memo = models.TextField(blank=True, verbose_name='배송 메모')
    
    error_message = models.TextField(blank=True, null=True, verbose_name='오류 메시지')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '주문'
        verbose_name_plural = '주문'

    def __str__(self):
        return f"주문 {self.order_no} ({self.shipper.name if self.shipper else 'N/A'})"

    def save(self, *args, **kwargs):
        # 주문번호가 없을 경우, 오늘 날짜 기반으로 자동 생성 (YYYYMMDD-XXXX)
        if not self.order_no:
            today = timezone.now().date()
            today_str = today.strftime('%Y%m%d')
            # 오늘 날짜로 생성된 마지막 주문을 찾습니다.
            last_order = Order.objects.filter(order_no__regex=r'^{}-\d+$'.format(today_str)).order_by('order_no').last()
            
            new_seq = 1
            if last_order:
                last_seq_str = last_order.order_no.split('-')[1]
                if last_seq_str.isdigit():
                    new_seq = int(last_seq_str) + 1
            
            # 새 주문번호를 생성합니다.
            self.order_no = f"{today_str}-{str(new_seq).zfill(4)}"
            
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    """
    하나의 주문에 포함된 개별 상품 정보를 담는 모델 (Order 모델과 1:N 관계)
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='주문')
    product = models.ForeignKey('management.Product', on_delete=models.PROTECT, verbose_name='상품')
    quantity = models.PositiveIntegerField(verbose_name='수량')
    
    class Meta:
        verbose_name = '주문 상품'
        verbose_name_plural = '주문 상품'
        
    def __str__(self):
        return f"{self.product.name} - {self.quantity}개"


class ApiCollectionLog(models.Model):
    """
    API 주문 수집 로그
    """
    LOG_STATUS_CHOICES = [
        ('SUCCESS', '성공'),
        ('PARTIAL', '부분 성공'),
        ('FAILED', '실패'),
    ]
    
    shipper = models.ForeignKey(
        'management.Shipper',
        on_delete=models.CASCADE,
        verbose_name='화주사'
    )
    channel_type = models.CharField(
        max_length=20,
        verbose_name='쇼핑몰'
    )
    collected_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='수집 시각'
    )
    status = models.CharField(
        max_length=20,
        choices=LOG_STATUS_CHOICES,
        default='SUCCESS',
        verbose_name='상태'
    )
    total_count = models.IntegerField(
        default=0,
        verbose_name='총 주문 수'
    )
    success_count = models.IntegerField(
        default=0,
        verbose_name='성공 건수'
    )
    error_count = models.IntegerField(
        default=0,
        verbose_name='실패 건수'
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='에러 메시지'
    )
    
    class Meta:
        verbose_name = 'API 수집 로그'
        verbose_name_plural = 'API 수집 로그'
        ordering = ['-collected_at']
    
    def __str__(self):
        return f"{self.shipper.name} - {self.channel_type} ({self.collected_at.strftime('%Y-%m-%d %H:%M')})"
