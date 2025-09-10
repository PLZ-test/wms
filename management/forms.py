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
        fields = ['name', 'barcode', 'width', 'length', 'height']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '가로'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '세로'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '높이'}),
        }