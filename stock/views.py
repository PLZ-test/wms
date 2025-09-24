# stock/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import F, Sum
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, date, timedelta
import json

from management.models import Product, Center
from .models import StockMovement, Location, WarehouseLayout
from .forms import StockInForm, StockUpdateForm, WarehouseLayoutForm

@login_required
@transaction.atomic
def stock_in_view(request):
    """
    재고 입고 페이지 뷰 (도면 '사용' 기능)
    - GET: 선택된 센터의 도면과 위치 정보를 불러와 페이지를 렌더링합니다.
    - POST: 모달 폼에서 제출된 입고 정보를 처리합니다.
    """
    selected_center_name = request.session.get('selected_center')
    center = None
    layout = None
    locations_json = "[]"
    
    # 사용자에게 상황을 명확히 알려주기 위한 상태 메시지 변수
    status_message = ""

    if selected_center_name:
        center = Center.objects.filter(name=selected_center_name).first()
        if center:
            try:
                # 선택된 센터에 해당하는 도면을 찾습니다.
                layout = WarehouseLayout.objects.get(center=center)
                # 해당 도면에 그려진 위치들을 모두 찾습니다.
                locations = Location.objects.filter(layout=layout)
                
                if locations.exists():
                    # [성공!] 도면과 위치가 모두 존재할 경우
                    locations_data = [{'id': loc.id, 'name': loc.name, 'x_coord': loc.x_coord, 'y_coord': loc.y_coord, 'width': loc.width, 'height': loc.height} for loc in locations]
                    locations_json = json.dumps(locations_data)
                    status_message = f"'{center.name}'의 '{layout.name}' 도면이 로드되었습니다. 입고할 위치를 클릭하세요."
                else:
                    # 도면은 있지만, 그려진 위치가 하나도 없는 경우
                    status_message = f"'{center.name}'의 도면은 있으나, 설정된 위치가 없습니다. [위치 편집] 페이지에서 위치를 먼저 그려주세요."
            except WarehouseLayout.DoesNotExist:
                # 센터는 선택했지만, 해당 센터에 등록된 도면이 없는 경우
                status_message = f"선택하신 '{center.name}'에는 등록된 도면이 없습니다. [도면 관리] 페이지에서 도면을 등록해주세요."
    else:
        # 상단 필터에서 '전체 센터'가 선택된 경우
        status_message = "입고 작업을 진행할 센터를 상단 필터에서 먼저 선택해주세요."


    if request.method == 'POST':
        form = StockInForm(request.POST, center_id=center.id if center else None)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            memo = form.cleaned_data['memo']
            location = form.cleaned_data['location']
            product.quantity = F('quantity') + quantity
            product.save()
            StockMovement.objects.create(
                product=product, location=location,
                movement_type='IN', quantity=quantity, memo=memo
            )
            messages.success(request, f"'{product.name}' {quantity}개 입고 처리 완료.")
            return redirect('stock:in_bound')
        else:
            messages.error(request, "입력값이 올바르지 않습니다. 모든 항목을 올바르게 선택했는지 확인해주세요.")
    else:
        form = StockInForm(center_id=center.id if center else None)

    context = {
        'page_title': '재고 입고',
        'form': form,
        'layout': layout,
        'locations_json': locations_json,
        'status_message': status_message, # 새로 만든 상태 메시지를 템플릿으로 전달
        'active_menu': 'inout'
    }
    return render(request, 'stock/stock_in.html', context)

@login_required
def layout_manage_view(request):
    """
    도면 관리 페이지 뷰 (목록 조회, 신규 등록, 삭제)
    """
    if request.method == 'POST':
        # 삭제 요청 처리
        if 'delete_layout' in request.POST:
            layout_id = request.POST.get('layout_id')
            layout = get_object_or_404(WarehouseLayout, pk=layout_id)
            layout.delete()
            messages.success(request, f'"{layout.name}" 도면이 삭제되었습니다.')
            return redirect('stock:layout_manage')
        
        # 신규 등록 처리
        form = WarehouseLayoutForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '새로운 도면이 성공적으로 등록되었습니다.')
            return redirect('stock:layout_manage')
    else:
        form = WarehouseLayoutForm()

    layouts = WarehouseLayout.objects.select_related('center').all()
    context = {
        'page_title': '도면 관리',
        'form': form,
        'layouts': layouts,
        'active_menu': 'inout'
    }
    return render(request, 'stock/layout_manage.html', context)

@login_required
def layout_editor_view(request, layout_id):
    """
    도면 위치 편집 페이지 뷰
    """
    layout = get_object_or_404(WarehouseLayout, pk=layout_id)
    context = {
        'page_title': f'"{layout.name}" 위치 편집',
        'layout': layout,
        'active_menu': 'inout'
    }
    return render(request, 'stock/layout_editor.html', context)

@login_required
def stock_manage_view(request):
    """
    현재 재고 현황을 리스트 형태로 보여주는 뷰
    """
    queryset = Product.objects.select_related('shipper__center').all()
    
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

@login_required
def stock_chart_data_api(request):
    """
    일별 입고량/출고량 데이터를 JSON 형태로 반환하는 API 뷰
    """
    start_str = request.GET.get('start'); end_str = request.GET.get('end')
    try:
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        end_date = date.today()
        start_date = end_date - timedelta(days=6)

    labels = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]
    
    movements = StockMovement.objects.filter(
        timestamp__date__range=[start_date, end_date]
    ).values('timestamp__date', 'movement_type').annotate(total_quantity=Sum('quantity')).order_by('timestamp__date')

    daily_data = {label: {'IN': 0, 'OUT': 0} for label in labels}
    for m in movements:
        date_str = m['timestamp__date'].strftime('%Y-%m-%d')
        if date_str in daily_data:
            daily_data[date_str][m['movement_type']] = m['total_quantity']
            
    datasets = [
        {
            'label': '입고량',
            'data': [daily_data[label]['IN'] for label in labels],
            'borderColor': 'rgba(54, 162, 235, 0.7)',
            'backgroundColor': 'rgba(54, 162, 235, 0.7)',
            'fill': False, 'tension': 0.1
        },
        {
            'label': '출고량',
            'data': [daily_data[label]['OUT'] for label in labels],
            'borderColor': 'rgba(255, 99, 132, 0.7)',
            'backgroundColor': 'rgba(255, 99, 132, 0.7)',
            'fill': False, 'tension': 0.1
        }
    ]
    return JsonResponse({'labels': labels, 'datasets': datasets})

@login_required
def location_api(request, layout_id):
    """
    도면(layout)에 속한 위치(location) 정보를 처리하는 API
    - GET: 해당 도면의 모든 위치 정보를 JSON으로 반환
    - POST: 새로운 위치 정보를 생성하거나 기존 위치 정보를 업데이트/삭제
    """
    layout = get_object_or_404(WarehouseLayout, pk=layout_id)
    
    if request.method == 'GET':
        locations = Location.objects.filter(layout=layout)
        data = [{
            'id': loc.id,
            'name': loc.name,
            'x_coord': loc.x_coord,
            'y_coord': loc.y_coord,
            'width': loc.width,
            'height': loc.height,
        } for loc in locations]
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action', 'save') # 'save' 또는 'delete'

            if action == 'delete':
                loc_id = data.get('id')
                Location.objects.filter(id=loc_id, layout=layout).delete()
                return JsonResponse({'status': 'success', 'message': '삭제되었습니다.'})

            # 'save' (생성 또는 업데이트)
            loc_name = data.get('name')
            if not loc_name:
                return JsonResponse({'status': 'error', 'message': '위치 이름이 필요합니다.'}, status=400)

            location, created = Location.objects.update_or_create(
                layout=layout,
                name=loc_name,
                defaults={
                    'x_coord': data['x_coord'],
                    'y_coord': data['y_coord'],
                    'width': data['width'],
                    'height': data['height'],
                }
            )
            return JsonResponse({'status': 'success', 'id': location.id, 'created': created})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': '잘못된 요청 방식입니다.'}, status=405)