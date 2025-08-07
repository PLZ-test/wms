from django.db import models

class Center(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='센터명')
    address = models.CharField(max_length=255, verbose_name='주소')

    def __str__(self):
        return self.name

class Shipper(models.Model):
    center = models.ForeignKey(Center, on_delete=models.CASCADE, verbose_name='소속 센터')
    name = models.CharField(max_length=100, unique=True, verbose_name='화주사명')
    contact = models.CharField(max_length=100, blank=True, verbose_name='담당자')

    def __str__(self):
        return self.name

class Courier(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='택배사명')
    contact = models.CharField(max_length=100, blank=True, verbose_name='연락처')

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

    def __str__(self):
        return f'[{self.shipper.name}] {self.name}'

class Order(models.Model):
    ORDER_STATUS_CHOICES = [('준비중', '준비중'), ('완료', '완료'), ('취소', '취소')]
    DELIVERY_STATUS_CHOICES = [('집하완료', '집하완료'), ('배송중', '배송중'), ('배송완료', '배송완료')]
    
    order_date = models.DateField(verbose_name='주문날짜')
    delivery_date = models.DateField(null=True, blank=True, verbose_name='배송날짜')
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='준비중')
    delivery_status = models.CharField(max_length=10, choices=DELIVERY_STATUS_CHOICES, blank=True)
    
    def __str__(self):
        return f"주문 {self.id} ({self.order_date})"

class StockMovement(models.Model):
    MOVEMENT_TYPES = [('IN', '입고'), ('OUT', '출고')]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='상품')
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES, verbose_name='구분')
    quantity = models.PositiveIntegerField(verbose_name='수량')
    memo = models.TextField(blank=True, verbose_name='메모')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='일시')

    def __str__(self):
        return f'[{self.get_movement_type_display()}] {self.product.name} - {self.quantity}개 ({self.timestamp})'