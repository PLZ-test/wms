# wms_app/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# --- 기존 모델 (Center, Shipper, User, Courier, Product) ---
class Center(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='센터명')
    address = models.CharField(max_length=255, verbose_name='주소')
    class Meta:
        verbose_name = '센터'
        verbose_name_plural = '센터'
    def __str__(self):
        return self.name

class Shipper(models.Model):
    center = models.ForeignKey(Center, on_delete=models.CASCADE, verbose_name='소속 센터')
    name = models.CharField(max_length=100, unique=True, verbose_name='화주사명')
    contact = models.CharField(max_length=100, blank=True, verbose_name='담당자')
    class Meta:
        verbose_name = '화주사'
        verbose_name_plural = '화주사'
    def __str__(self):
        return self.name

class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        CENTER_ADMIN = 'CENTER_ADMIN', '센터 관리자'
        CENTER_MANAGER = 'CENTER_MANAGER', '센터 매니저'
        CENTER_MEMBER = 'CENTER_MEMBER', '센터 구성원'
        SHIPPER_ADMIN = 'SHIPPER_ADMIN', '화주사 관리자'
        SHIPPER_MANAGER = 'SHIPPER_MANAGER', '화주사 매니저'
        SHIPPER_MEMBER = 'SHIPPER_MEMBER', '화주사 구성원'
        UNASSIGNED = 'UNASSIGNED', '미지정'
    role = models.CharField(max_length=20, choices=RoleChoices.choices, default='UNASSIGNED', verbose_name='사용자 역할')
    center = models.ForeignKey(Center, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='소속 센터')
    shipper = models.ForeignKey(Shipper, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='소속 화주사')
    groups = models.ManyToManyField('auth.Group', verbose_name='groups', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='wms_app_user_groups', related_query_name='wms_app_user')
    user_permissions = models.ManyToManyField('auth.Permission', verbose_name='user permissions', blank=True, help_text='Specific permissions for this user.', related_name='wms_app_user_permissions', related_query_name='wms_app_user')
    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자'

class Courier(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='택배사명')
    contact = models.CharField(max_length=100, blank=True, verbose_name='연락처')
    class Meta:
        verbose_name = '택배사'
        verbose_name_plural = '택배사'
    def __str__(self):
        return self.name

class Product(models.Model):
    shipper = models.ForeignKey(Shipper, on_delete=models.CASCADE, verbose_name='화주사')
    name = models.CharField(max_length=200, verbose_name='상품명')
    barcode = models.CharField(max_length=100, unique=True, verbose_name='바코드')
    width = models.FloatField(default=0, verbose_name='가로(cm)')
    length = models.FloatField(default=0, verbose_name='세로(cm)')
    height = models.FloatField(default=0, verbose_name='높이(cm)')
    quantity = models.PositiveIntegerField(default=0, verbose_name='재고 수량')
    class Meta:
        verbose_name = '상품'
        verbose_name_plural = '상품'
    def __str__(self):
        return f'[{self.shipper.name}] {self.name}'

class SalesChannel(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='판매 채널명')
    class Meta:
        verbose_name = '판매 채널'
        verbose_name_plural = '판매 채널'
    def __str__(self):
        return self.name

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', '주문접수'),
        ('PROCESSING', '처리중'),
        ('SHIPPED', '출고완료'),
        ('DELIVERED', '배송완료'),
        ('CANCELED', '주문취소'),
        ('ERROR', '오류'),
    ]

    shipper = models.ForeignKey(Shipper, on_delete=models.SET_NULL, null=True, verbose_name='화주사')
    channel = models.ForeignKey(SalesChannel, on_delete=models.SET_NULL, null=True, verbose_name='판매 채널')
    order_no = models.CharField(max_length=100, verbose_name='주문번호', null=True, blank=True, unique=True)
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
        if not self.order_no:
            today = timezone.now().date()
            today_str = today.strftime('%Y%m%d')
            
            # --- [수정] 주문번호 자동 생성 로직 변경 ---
            # 오늘 날짜와 '-' 그리고 숫자로만 이루어진 주문번호를 찾도록 정규식(regex)을 사용합니다.
            last_order = Order.objects.filter(order_no__regex=r'^{}-\d+$'.format(today_str)).order_by('order_no').last()
            
            if last_order:
                # 마지막 주문번호에서 순번 부분을 추출하여 1 증가시킵니다.
                last_seq_str = last_order.order_no.split('-')[1]
                # 혹시 모를 비정상적인 데이터에 대비하여, 순번 부분이 숫자인지 한번 더 확인합니다.
                if last_seq_str.isdigit():
                    new_seq = int(last_seq_str) + 1
                else:
                    new_seq = 1 # 숫자가 아니면 1번부터 다시 시작
            else:
                # 오늘 첫 주문인 경우 1번으로 시작합니다.
                new_seq = 1
            
            # YYYYMMDD-XXXX 형식으로 새로운 주문번호를 생성합니다.
            self.order_no = f"{today_str}-{str(new_seq).zfill(4)}"
            # -------------------------------------------
            
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='주문')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='상품')
    quantity = models.PositiveIntegerField(verbose_name='수량')
    class Meta:
        verbose_name = '주문 상품'
        verbose_name_plural = '주문 상품'
    def __str__(self):
        return f"{self.product.name} - {self.quantity}개"

class StockMovement(models.Model):
    MOVEMENT_TYPES = [('IN', '입고'), ('OUT', '출고')]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='상품')
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES, verbose_name='구분')
    quantity = models.PositiveIntegerField(verbose_name='수량')
    memo = models.TextField(blank=True, verbose_name='메모')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='일시')
    class Meta:
        verbose_name = '재고 이동 기록'
        verbose_name_plural = '재고 이동 기록'
    def __str__(self):
        return f'[{self.get_movement_type_display()}] {self.product.name} - {self.quantity}개 ({self.timestamp})'