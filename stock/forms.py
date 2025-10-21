# stock/forms.py
from django import forms
from management.models import Product
from .models import Location, StockMovement

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['zone', 'name', 'max_floor', 'description']
        labels = { 'zone': '구역명', 'name': '위치명', 'max_floor': '최대 층수', 'description': '설명' }
        widgets = {
            'zone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '예: A구역, B구역'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '예: A-01, B-01'}),
            'max_floor': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class StockInForm(forms.Form):
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
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '입고할 층 번호'})
    )
    # --- [삭제] 'box_size' 필드를 폼에서 완전히 제거합니다. ---
    
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
        widgets = { 'quantity': forms.NumberInput(attrs={'class': 'form-control'}) }
        labels = { 'quantity': '재고 수량' }