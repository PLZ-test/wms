# settlement/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def settlement_status_view(request):
    """
    '정산 현황' 페이지를 보여주는 뷰 (현재는 준비 중 페이지)
    """
    context = {
        'page_title': '정산 현황',
        'active_menu': 'settlement'
    }
    return render(request, 'settlement/placeholder_page.html', context)

@login_required
def settlement_billing_view(request):
    """
    '정산 청구내역' 페이지를 보여주는 뷰 (현재는 준비 중 페이지)
    """
    context = {
        'page_title': '정산 청구내역',
        'active_menu': 'settlement'
    }
    return render(request, 'settlement/placeholder_page.html', context)

@login_required
def settlement_config_view(request):
    """
    '정산내역설정' 페이지를 보여주는 뷰 (현재는 준비 중 페이지)
    """
    context = {
        'page_title': '정산내역설정',
        'active_menu': 'settlement'
    }
    return render(request, 'settlement/placeholder_page.html', context)