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
        fields = ['name', 'barcode', 'width', 'length', 'height']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '가로'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '세로'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '높이'}),
        }

class StockIOForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label="상품 선택", empty_label="상품을 선택하세요")
    quantity = forms.IntegerField(min_value=1, label="수량")
    memo = forms.CharField(label="메모", widget=forms.Textarea(attrs={'rows': 3}), required=False)

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