# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    """
    회원가입을 위한 커스텀 폼입니다.
    기본 UserCreationForm을 상속받아 아이디와 이메일만 입력받도록 수정합니다.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email') # 회원가입 시 받을 필드

    def save(self, commit=True):
        user = super().save(commit=False)
        # 회원가입 시 사용자를 비활성(is_active=False) 상태로 만듭니다. 관리자 승인이 필요합니다.
        user.is_active = False
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    """
    관리자가 사용자의 역할 및 소속 정보를 수정하기 위한 폼입니다.
    """
    class Meta:
        model = User
        fields = ['role', 'center', 'shipper'] # 수정할 필드
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