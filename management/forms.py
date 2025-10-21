# management/forms.py
from django import forms
from .models import Center, Shipper, Courier, Product

class CenterForm(forms.ModelForm):
    class Meta:
        model = Center
        fields = ['name', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ShipperForm(forms.ModelForm):
    class Meta:
        model = Shipper
        fields = ['name', 'contact', 'center']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'center': forms.Select(attrs={'class': 'form-control'}),
        }

class CourierForm(forms.ModelForm):
    class Meta:
        model = Courier
        fields = ['name', 'contact']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # --- [수정] 'box_size' 필드를 폼에 포함시킵니다. ---
        fields = ['name', 'barcode', 'width', 'length', 'height', 'quantity', 'products_per_pallet', 'pallet_quantity', 'box_size']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '가로'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '세로'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '높이'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'products_per_pallet': forms.NumberInput(attrs={'class': 'form-control'}),
            'pallet_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            # --- [추가] 'box_size' 필드의 위젯을 Select(선택 상자)로 지정합니다. ---
            'box_size': forms.Select(attrs={'class': 'form-control'}),
        }

class ProductCreateDirectForm(forms.ModelForm):
    class Meta:
        model = Product
        # --- [수정] 'box_size' 필드를 이 폼에도 포함시킵니다. ---
        fields = ['shipper', 'name', 'barcode', 'width', 'length', 'height', 'quantity', 'products_per_pallet', 'pallet_quantity', 'box_size']
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
            # --- [추가] 'box_size' 필드의 위젯을 지정합니다. ---
            'box_size': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'shipper': '화주사 선택'
        }