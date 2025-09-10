# orders/forms.py
from django import forms
from .models import Order

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