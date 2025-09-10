# stock/forms.py
from django import forms
from management.models import Product # management 앱의 Product 모델을 가져옵니다.

class StockIOForm(forms.Form):
    """
    재고 입고/출고 처리를 위한 폼
    """
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label="상품 선택", empty_label="상품을 선택하세요")
    quantity = forms.IntegerField(min_value=1, label="수량")
    memo = forms.CharField(label="메모", widget=forms.Textarea(attrs={'rows': 3}), required=False)

class StockUpdateForm(forms.ModelForm):
    """
    재고 현황 페이지에서 개별 상품의 재고 수량을 직접 수정하기 위한 폼
    """
    class Meta:
        model = Product
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'quantity': '재고 수량'
        }