from django.db import models
from django.contrib.auth.models import AbstractUser

class Center(models.Model):
    """
    물류 창고 센터 정보를 저장하는 모델.
    name: 센터명, address: 센터 주소
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
    화주사(상품 판매자) 정보를 저장하는 모델.
    center: 소속 센터, name: 화주사명, contact: 담당자 연락처
    """
    center = models.ForeignKey(Center, on_delete=models.CASCADE, verbose_name='소속 센터')
    name = models.CharField(max_length=100, unique=True, verbose_name='화주사명')
    contact = models.CharField(max_length=100, blank=True, verbose_name='담당자')

    class Meta:
        verbose_name = '화주사'
        verbose_name_plural = '화주사'

    def __str__(self):
        return self.name

class User(AbstractUser):
    """
    사용자 정보를 저장하는 커스텀 모델.
    role: 사용자 역할, center: 소속 센터, shipper: 소속 화주사
    """
    class RoleChoices(models.TextChoices):
        CENTER_ADMIN = 'CENTER_ADMIN', '센터 관리자'
        CENTER_MANAGER = 'CENTER_MANAGER', '센터 매니저'
        CENTER_MEMBER = 'CENTER_MEMBER', '센터 구성원'
        SHIPPER_ADMIN = 'SHIPPER_ADMIN', '화주사 관리자'
        SHIPPER_MANAGER = 'SHIPPER_MANAGER', '화주사 매니저'
        SHIPPER_MEMBER = 'SHIPPER_MEMBER', '화주사 구성원'
        UNASSIGNED = 'UNASSIGNED', '미지정'

    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.UNASSIGNED, verbose_name='사용자 역할')
    center = models.ForeignKey(Center, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='소속 센터')
    shipper = models.ForeignKey(Shipper, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='소속 화주사')

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자'


class Courier(models.Model):
    """
    택배사 정보를 저장하는 모델.
    name: 택배사명, contact: 연락처
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
    상품 정보를 저장하는 모델.
    shipper: 화주사, name: 상품명, barcode: 바코드, width/length/height: 크기, quantity: 재고 수량
    """
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

class Order(models.Model):
    """
    주문 정보를 저장하는 모델.
    order_date: 주문날짜, delivery_date: 배송날짜, order_status: 주문 상태, delivery_status: 배송 상태
    """
    ORDER_STATUS_CHOICES = [('준비중', '준비중'), ('완료', '완료'), ('취소', '취소')]
    DELIVERY_STATUS_CHOICES = [('집하완료', '집하완료'), ('배송중', '배송중'), ('배송완료', '배송완료')]
    
    order_date = models.DateField(verbose_name='주문날짜')
    delivery_date = models.DateField(null=True, blank=True, verbose_name='배송날짜')
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='준비중')
    delivery_status = models.CharField(max_length=10, choices=DELIVERY_STATUS_CHOICES, blank=True)
    
    class Meta:
        verbose_name = '주문'
        verbose_name_plural = '주문'

    def __str__(self):
        return f"주문 {self.id} ({self.order_date})"

class StockMovement(models.Model):
    """
    재고 이동 기록을 저장하는 모델. (입고/출고)
    product: 상품, movement_type: 구분, quantity: 수량, memo: 메모, timestamp: 기록 일시
    """
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