# stock/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import F, Sum, Count, Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from datetime import datetime, date, timedelta
from collections import defaultdict

from management.models import Product, Center
from .models import StockMovement, Location
from .forms import StockInForm, StockUpdateForm, LocationForm

@login_required
@transaction.atomic
def stock_in_view(request):
    """
    재고 입고 페이지 뷰 (탭 없는 단일 그리드 UI)
    """
    selected_center_name = request.session.get('selected_center')
    center = None
    locations_with_status = []
    status_message = ""

    if selected_center_name:
        center = Center.objects.filter(name=selected_center_name).first()
        if center:
            locations = Location.objects.filter(center=center).order_by('name')
            
            if locations.exists():
                stock_data = StockMovement.objects.filter(
                    location__in=locations,
                    movement_type='IN'
                ).values(
                    'location_id', 'floor', 'product__name'
                ).annotate(
                    total_quantity=Sum('quantity')
                )
                
                stocks_by_location = defaultdict(lambda: defaultdict(dict))
                for stock in stock_data:
                    stocks_by_location[stock['location_id']][stock['floor']][stock['product__name']] = stock['total_quantity']

                for loc in locations:
                    floors_status = []
                    for i in range(1, loc.max_floor + 1):
                        stock_info = stocks_by_location[loc.id].get(i, {})
                        floors_status.append({
                            'floor_number': i,
                            'stock_info': stock_info,
                            'is_stocked': bool(stock_info)
                        })
                        
                    locations_with_status.append({
                        'id': loc.id,
                        'name': loc.name,
                        'max_floor': loc.max_floor,
                        'floors': floors_status
                    })
                status_message = f"'{center.name}'의 재고 현황이 로드되었습니다. 입고할 위치를 클릭하세요."
            else:
                status_message = f"'{center.name}'에 등록된 재고 위치가 없습니다. [재고 위치 관리] 메뉴에서 위치를 먼저 등록해주세요."
    else:
        status_message = "입고 작업을 진행할 센터를 상단 필터에서 먼저 선택해주세요."

    if request.method == 'POST':
        location_id = request.POST.get('location')
        floor_num = request.POST.get('floor')
        form = StockInForm(request.POST)

        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            memo = form.cleaned_data['memo']
            
            try:
                location_obj = Location.objects.get(pk=location_id)

                product.quantity = F('quantity') + quantity
                product.save(update_fields=['quantity'])

                StockMovement.objects.create(
                    product=product,
                    location=location_obj,
                    movement_type='IN',
                    quantity=quantity,
                    floor=floor_num,
                    box_size=product.box_size,
                    memo=memo
                )
                messages.success(request, f"'{product.name}' {quantity}개 입고 처리 완료 (위치: {location_obj.name}, {floor_num}층).")
                return redirect('stock:in_bound')
            except Location.DoesNotExist:
                messages.error(request, "선택된 위치 정보를 찾을 수 없습니다.")
        else:
            error_str = " ".join([f"{field}: {error[0]}" for field, error in form.errors.items()])
            messages.error(request, f"입력값이 올바르지 않습니다. ({error_str})")
    else:
        form = StockInForm()

    context = {
        'page_title': '재고 입고',
        'form': form,
        'locations': locations_with_status,
        'status_message': status_message,
        'active_menu': 'inout'
    }
    return render(request, 'stock/stock_in.html', context)


@login_required
def location_manage_view(request):
    """
    재고 위치 관리 뷰 (자동 생성 로직 추가 및 모달 기반으로 변경)
    """
    selected_center_name = request.session.get('selected_center')
    
    if not selected_center_name:
        messages.error(request, '먼저 상단 필터에서 작업을 진행할 센터를 선택해주세요.')
        return render(request, 'stock/location_manage.html', {'page_title': '재고 위치 관리', 'locations': Location.objects.none(), 'form': LocationForm()})

    try:
        center = Center.objects.get(name=selected_center_name)
    except Center.DoesNotExist:
        messages.error(request, '선택된 센터를 찾을 수 없습니다.')
        return redirect('core:dashboard') 

    if not Location.objects.filter(center=center).exists():
        default_locations = [chr(c) for c in range(ord('A'), ord('I') + 1)]
        with transaction.atomic():
            for loc_name in default_locations:
                Location.objects.create(center=center, zone='기본', name=loc_name, max_floor=1)
        messages.info(request, f"'{center.name}'에 기본 위치(A ~ I)가 자동으로 생성되었습니다.")

    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.center = center
            location.save()
            messages.success(request, '새로운 재고 위치가 등록되었습니다.')
            return redirect('stock:location_manage')
        else:
            locations = Location.objects.filter(center=center).order_by('zone', 'name')
            context = {
                'page_title': '재고 위치 관리',
                'locations': locations,
                'form': form,
                'active_menu': 'inout',
                'form_errors': True
            }
            return render(request, 'stock/location_manage.html', context)

    locations = Location.objects.filter(center=center).order_by('zone', 'name')
    form = LocationForm()
    context = {
        'page_title': '재고 위치 관리',
        'locations': locations,
        'form': form,
        'active_menu': 'inout'
    }
    return render(request, 'stock/location_manage.html', context)

@login_required
@require_POST
def location_update_view(request, pk):
    location = get_object_or_404(Location, pk=pk)
    form = LocationForm(request.POST, instance=location)
    if form.is_valid():
        form.save()
        messages.success(request, '재고 위치 정보가 수정되었습니다.')
    else:
        messages.error(request, '수정 중 오류가 발생했습니다. 입력값을 확인해주세요.')
    return redirect('stock:location_manage')

@login_required
@require_POST
def location_delete_view(request, pk):
    location = get_object_or_404(Location, pk=pk)
    location.delete()
    messages.success(request, '재고 위치가 삭제되었습니다.')
    return redirect('stock:location_manage')

@login_required
def stock_manage_view(request):
    queryset = Product.objects.select_related('shipper__center').all()
    selected_center = request.session.get('selected_center')
    selected_shipper = request.session.get('selected_shipper')
    if selected_center:
        queryset = queryset.filter(shipper__center__name=selected_center)
    if selected_shipper:
        queryset = queryset.filter(shipper__name=selected_shipper)
    context = {'page_title': '재고 현황', 'product_list': queryset, 'active_menu': 'management'}
    return render(request, 'stock/stock_list.html', context)

@login_required
def stock_update_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('stock:manage')
    else:
        form = StockUpdateForm(instance=product)
    context = {'form': form, 'product': product, 'page_title': '재고 수량 수정', 'active_menu': 'management'}
    return render(request, 'stock/stock_update_form.html', context)

@login_required
def stock_movement_history_view(request):
    movements = StockMovement.objects.select_related('product__shipper', 'location').order_by('-timestamp')
    context = {'page_title': '입출고 기록', 'movements': movements, 'active_menu': 'inout'}
    return render(request, 'stock/stock_history.html', context)

@login_required
def stock_chart_data_api(request):
    start_str = request.GET.get('start'); end_str = request.GET.get('end')
    try:
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
    labels = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]
    movements = StockMovement.objects.filter(timestamp__date__range=[start_date, end_date]).values('timestamp__date', 'movement_type').annotate(total_quantity=Sum('quantity')).order_by('timestamp__date')
    daily_data = {label: {'IN': 0, 'OUT': 0} for label in labels}
    for m in movements:
        date_str = m['timestamp__date'].strftime('%Y-%m-%d')
        if date_str in daily_data:
            daily_data[date_str][m['movement_type']] = m['total_quantity']
    datasets = [{'label': '입고량', 'data': [daily_data[label]['IN'] for label in labels], 'borderColor': 'rgba(54, 162, 235, 0.7)', 'backgroundColor': 'rgba(54, 162, 235, 0.7)', 'fill': False, 'tension': 0.1}, {'label': '출고량', 'data': [daily_data[label]['OUT'] for label in labels], 'borderColor': 'rgba(255, 99, 132, 0.7)', 'backgroundColor': 'rgba(255, 99, 132, 0.7)', 'fill': False, 'tension': 0.1}]
    return JsonResponse({'labels': labels, 'datasets': datasets})