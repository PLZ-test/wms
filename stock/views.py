# stock/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, F
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # <--- 이 줄이 추가되었습니다!

from management.models import Product # management 앱의 Product 모델
from .models import StockMovement
from .forms import StockIOForm, StockUpdateForm

@login_required
def stock_manage_view(request):
    """
    현재 재고 현황을 리스트 형태로 보여주는 뷰
    """
    # Product 모델의 데이터를 가져오되, 연관된 shipper와 center 정보를 함께 조회하여 성능 최적화
    queryset = Product.objects.select_related('shipper__center').all()
    
    # 세션에 저장된 필터 값으로 데이터 필터링
    selected_center = request.session.get('selected_center')
    selected_shipper = request.session.get('selected_shipper')
    if selected_center:
        queryset = queryset.filter(shipper__center__name=selected_center)
    if selected_shipper:
        queryset = queryset.filter(shipper__name=selected_shipper)
        
    context = {
        'page_title': '재고 현황',
        'product_list': queryset,
        'active_menu': 'management',
    }
    return render(request, 'stock/stock_list.html', context)

@login_required
@transaction.atomic # 데이터베이스 트랜잭션 처리
def stock_io_view(request):
    """
    재고 입고 및 출고를 처리하는 뷰
    """
    if request.method == 'POST':
        form_data = request.POST.copy()
        form = StockIOForm(form_data)
        
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            memo = form.cleaned_data['memo']
            io_type = request.POST.get('io_type') # 'in' 또는 'out'

            if io_type == 'in':
                # 입고 처리: 상품 수량을 증가시키고 입고 기록을 남김
                product.quantity = F('quantity') + quantity
                movement_type = 'IN'
                messages.success(request, f"'{product.name}' {quantity}개 입고 처리 완료.")
            elif io_type == 'out':
                # 출고 처리
                product.refresh_from_db() # 최신 재고 수량을 DB에서 다시 불러옴
                if product.quantity < quantity:
                    messages.error(request, f"재고 부족: '{product.name}'의 현재 재고({product.quantity}개)보다 많이 출고할 수 없습니다.")
                    return redirect('stock:io')
                
                product.quantity = F('quantity') - quantity
                movement_type = 'OUT'
                messages.success(request, f"'{product.name}' {quantity}개 출고 처리 완료.")
            
            product.save()
            StockMovement.objects.create(
                product=product,
                movement_type=movement_type,
                quantity=quantity,
                memo=memo
            )
            return redirect('stock:io')
        else:
            messages.error(request, "입력값이 올바르지 않습니다.")

    # GET 요청 시 보여줄 입출고 페이지
    products = Product.objects.select_related('shipper__center').all()
    selected_center = request.session.get('selected_center')
    selected_shipper = request.session.get('selected_shipper')
    if selected_center:
        products = products.filter(shipper__center__name=selected_center)
    if selected_shipper:
        products = products.filter(shipper__name=selected_shipper)
        
    context = {
        'page_title': '재고 입출고',
        'products': products,
        'active_menu': 'inout'
    }
    return render(request, 'stock/stock_io.html', context)

@login_required
def stock_update_view(request, pk):
    """
    재고 현황 목록에서 특정 상품의 재고를 직접 수정하는 뷰
    """
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('stock:manage')
    else:
        form = StockUpdateForm(instance=product)
        
    context = {
        'form': form,
        'product': product,
        'page_title': '재고 수량 수정',
        'active_menu': 'management'
    }
    return render(request, 'stock/stock_update_form.html', context)

@login_required
def stock_movement_history_view(request):
    """
    전체 재고 이동(입출고) 기록을 보여주는 뷰
    """
    movements = StockMovement.objects.select_related('product__shipper').order_by('-timestamp')
    context = {
        'page_title': '입출고 기록',
        'movements': movements,
        'active_menu': 'inout'
    }
    return render(request, 'stock/stock_history.html', context)