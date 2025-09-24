# stock/forms.py
from django import forms
from management.models import Product
from .models import Location, WarehouseLayout # [추가] WarehouseLayout 모델 import

# [신규] 도면 업로드를 위한 ModelForm
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
    # ... 기존 StockInForm 코드는 그대로 유지 ...
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="상품 선택",
        empty_label="상품을 선택하세요"
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        label="입고 위치",
        empty_label="위치를 선택하세요"
    )
    quantity = forms.IntegerField(min_value=1, label="수량")
    memo = forms.CharField(label="메모", widget=forms.Textarea(attrs={'rows': 3}), required=False)

    def __init__(self, *args, **kwargs):
        center_id = kwargs.pop('center_id', None)
        super().__init__(*args, **kwargs)
        if center_id:
            # location 필드는 더 이상 form에서 직접 사용하지 않으므로 queryset 설정이 불필요할 수 있습니다.
            # 하지만 유효성 검사를 위해 유지합니다.
            try:
                layout = WarehouseLayout.objects.get(center_id=center_id)
                self.fields['location'].queryset = Location.objects.filter(layout=layout)
            except WarehouseLayout.DoesNotExist:
                self.fields['location'].queryset = Location.objects.none()


class StockUpdateForm(forms.ModelForm):
    # ... 기존 StockUpdateForm 코드는 그대로 유지 ...
    class Meta:
        model = Product
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'quantity': '재고 수량'
        }