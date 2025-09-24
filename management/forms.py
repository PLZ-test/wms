# management/forms.py
from django import forms
from .models import Center, Shipper, Courier, Product

class CenterForm(forms.ModelForm):
    """
    센터 생성을 위한 폼
    """
    class Meta:
        model = Center
        fields = ['name', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ShipperForm(forms.ModelForm):
    """
    화주사 생성을 위한 폼
    """
    class Meta:
        model = Shipper
        fields = ['name', 'contact', 'center']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'center': forms.Select(attrs={'class': 'form-control'}),
        }

class CourierForm(forms.ModelForm):
    """
    택배사 생성을 위한 폼
    """
    class Meta:
        model = Courier
        fields = ['name', 'contact']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
class ProductForm(forms.ModelForm):
    """
    상품 생성을 위한 폼
    """
    class Meta:
        model = Product
        # --- [수정] 폼에 포함될 필드 목록 변경 ---
        fields = ['name', 'barcode', 'width', 'length', 'height', 'quantity', 'products_per_pallet', 'pallet_quantity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '가로'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '세로'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '높이'}),
            # --- [추가] 새로운 필드들의 위젯 설정 ---
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'products_per_pallet': forms.NumberInput(attrs={'class': 'form-control'}),
            'pallet_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# --- [추가] 대시보드에서 직접 상품을 등록하기 위한 새로운 폼 ---
class ProductCreateDirectForm(forms.ModelForm):
    """
    대시보드에서 화주사를 선택하며 상품을 바로 등록하기 위한 폼
    """
    class Meta:
        model = Product
        # 기존 ProductForm 필드에 'shipper' 필드를 추가합니다.
        fields = ['shipper', 'name', 'barcode', 'width', 'length', 'height', 'quantity', 'products_per_pallet', 'pallet_quantity']
        widgets = {
            'shipper': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '가로'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '세로'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '높이'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'products_per_pallet': forms.NumberInput(attrs={'class': 'form-control'}),
            'pallet_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'shipper': '화주사 선택' # 화주사 필드의 라벨을 지정합니다.
        }
# -----------------------------------------------------------