# core/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """
    메인 대시보드(홈) 화면을 렌더링합니다.
    4개의 메인 메뉴 카드를 보여줍니다.
    """
    context = {
        'page_title': '홈',
        'active_menu': 'dashboard' # 현재 메뉴 활성화를 위한 값 (사용하지 않을 경우 삭제 가능)
    }
    return render(request, 'core/dashboard.html', context)