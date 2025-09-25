# stock/forms.py
from django import forms
from management.models import Product
from .models import Location, WarehouseLayout, StockMovement # StockMovement 모델 import

class WarehouseLayoutForm(forms.ModelForm):
    class Meta:
        model = WarehouseLayout
        fields = ['center', 'name', 'image']
        labels = {
            'center': '소속 센터',
            'name': '도면명',
            'image': '도면 이미지 파일',
        }
        widgets = {
            'center': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class StockInForm(forms.Form):
    # 입고 처리 폼
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="상품 선택",
        empty_label="상품을 선택하세요",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        min_value=1, 
        label="수량",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    floor = forms.IntegerField(
        min_value=1, 
        label="층",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '몇 층에 적재할까요?'})
    )
    box_size = forms.ChoiceField(
        choices=StockMovement.BOX_SIZE_CHOICES,
        label="박스 크기",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    memo = forms.CharField(
        label="메모", 
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), 
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'quantity': '재고 수량'
        }