from django import forms
from django.contrib.auth.forms import UserCreationForm
# --- [수정] Order 모델을 import합니다. ---
from .models import Center, Shipper, Courier, Product, User, Order

# --- [추가] 회원가입 폼 ---
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email') # 회원가입 시 아이디와 이메일만 받도록 설정

    def save(self, commit=True):
        user = super().save(commit=False)
        # 회원가입 시 사용자를 비활성 상태로 만듭니다.
        user.is_active = False
        if commit:
            user.save()
        return user

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

# --- [신규] 오류 주문 수정을 위한 폼 ---
class OrderUpdateForm(forms.ModelForm):
    """
    오류가 발생한 주문의 정보를 수정하기 위한 폼입니다.
    수취인명, 연락처, 주소 필드만 수정 가능하도록 설정합니다.
    """
    class Meta:
        model = Order
        # 수정이 필요한 필드 목록
        fields = ['recipient_name', 'recipient_phone', 'address']
        # 각 필드에 대한 라벨(화면에 표시될 이름) 설정
        labels = {
            'recipient_name': '수취인명',
            'recipient_phone': '연락처',
            'address': '주소',
        }
        # HTML 폼 위젯 설정 (CSS 클래스 적용 등)
        widgets = {
            'recipient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'recipient_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }
# ------------------------------------

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

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['role', 'center', 'shipper']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'center': forms.Select(attrs={'class': 'form-control'}),
            'shipper': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'role': '사용자 역할',
            'center': '소속 센터',
            'shipper': '소속 화주사',
        }