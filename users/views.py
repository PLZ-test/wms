# users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import JsonResponse

# [수정] 모델과 폼을 현재 앱(users)과 다른 앱(management)에서 가져오도록 경로를 수정합니다.
from .models import User
from .forms import CustomUserCreationForm, UserUpdateForm

# --- 인증 관련 뷰 ---

class CustomLoginView(LoginView):
    """
    # 커스텀 로그인 뷰
    # 기본 LoginView를 상속받아, 로그인 실패 메시지나 비활성 계정 처리 등 추가 로직을 구현합니다.
    """
    # 사용할 템플릿을 지정합니다.
    template_name = 'registration/login.html'

    def form_invalid(self, form):
        # 폼 유효성 검증에 실패했을 때 (ID/PW 불일치 등) 에러 메시지를 추가합니다.
        messages.error(self.request, '아이디 또는 비밀번호가 올바르지 않습니다.')
        return super().form_invalid(form)

    def form_valid(self, form):
        # 폼 유효성 검증에 성공했을 때
        user = form.get_user()
        if not user.is_active:
            # 사용자가 활성(승인) 상태가 아니면 에러 메시지를 표시하고 로그인시키지 않습니다.
            messages.error(self.request, '아직 승인되지 않은 계정입니다. 관리자에게 문의하세요.')
            return self.form_invalid(form)
        return super().form_valid(form)

@login_required
def wms_logout_view(request):
    """
    # 로그아웃 뷰
    # 사용자를 로그아웃시키고 로그인 페이지로 리디렉션합니다.
    """
    logout(request)
    # [수정] 로그아웃 후 'users:login' URL 이름으로 리디렉션합니다.
    return redirect('users:login')

def signup_view(request):
    """
    # 회원가입 뷰
    # 회원가입 폼을 보여주고, 유효한 데이터가 제출되면 사용자를 생성합니다.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # [수정] 회원가입 완료 페이지로 리디렉션합니다.
            return redirect('users:signup_done')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def signup_done_view(request):
    """
    # 회원가입 완료 안내 페이지 뷰
    """
    return render(request, 'registration/signup_done.html')

# --- 사용자 관리 뷰 ---

@login_required
def user_manage_view(request):
    """
    # 사용자 관리 목록 뷰
    # 가입 요청한 비활성(is_active=False) 사용자 목록을 보여줍니다.
    """
    # [수정] is_active=False 필터를 추가하여 승인 대기 중인 사용자만 표시합니다.
    user_list = User.objects.filter(is_superuser=False, is_active=False)
    context = {
        'page_title': '사용자 관리 (가입 승인)',
        'active_menu': 'management', # 사이드바 메뉴 활성화를 위함
        'user_list': user_list,
    }
    return render(request, 'users/user_list.html', context)

@login_required
def user_update_view(request, pk):
    """
    # 사용자 정보 수정(역할 부여 및 승인) 뷰
    """
    user_instance = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_instance)
        if form.is_valid():
            updated_user = form.save(commit=False)
            # [추가] 역할을 부여받으면 is_active를 True로 변경하여 계정을 활성화(승인)합니다.
            updated_user.is_active = True
            updated_user.save()
            # [수정] 사용자 관리 목록 페이지로 리디렉션합니다.
            return redirect('users:manage')
    else:
        form = UserUpdateForm(instance=user_instance)
    context = {
        'form': form,
        'target_user': user_instance,
        'page_title': '사용자 역할 부여 및 가입 승인',
        'active_menu': 'management'
    }
    return render(request, 'users/user_form.html', context)


# --- API 뷰 ---

def check_username_api(request):
    """
    # 회원가입 시 사용자 이름 중복을 실시간으로 확인하는 API
    """
    username = request.GET.get('username', None)
    is_taken = User.objects.filter(username__iexact=username).exists()
    data = {'is_available': not is_taken}
    return JsonResponse(data)
