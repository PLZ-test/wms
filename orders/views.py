# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.db.models import Count, Q, F # [수정] F객체 추가
from datetime import datetime, date, timedelta
from django.db.models.functions import TruncDate
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
import openpyxl
import json

from management.models import Shipper, Product, SalesChannel
from stock.models import StockMovement # [추가] StockMovement 모델 import
from .models import Order, OrderItem
from .forms import OrderUpdateForm

# ... (order_manage_view, order_list_success_view 등 다른 뷰는 그대로 유지) ...
@login_required
def order_manage_view(request):
    """
    일자별 주문 관리 대시보드 뷰
    """
    date_str = request.GET.get('date')
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    
    orders_for_date = Order.objects.filter(order_date__date=selected_date)
    
    success_count = orders_for_date.exclude(order_status='ERROR').count()
    error_count_db = orders_for_date.filter(order_status='ERROR').count()
    
    temp_errors_count = len(request.session.get('temp_errors', []))
    total_count = success_count + error_count_db + temp_errors_count
    error_count = error_count_db + temp_errors_count
    
    daily_stats = {
        'total_count': total_count,
        'success_count': success_count,
        'error_count': error_count,
        'success_rate': (success_count / total_count * 100) if total_count > 0 else 0,
        'error_rate': (error_count / total_count * 100) if total_count > 0 else 0,
    }
    context = {
        'page_title': '주문 관리',
        'active_menu': 'orders',
        'selected_date': selected_date.strftime('%Y-%m-%d'),
        'daily_stats': daily_stats,
    }
    return render(request, 'orders/order_manage.html', context)

@login_required
def order_list_success_view(request, date_str):
    """
    선택한 날짜의 '성공' 주문 목록을 보여주는 뷰
    """
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    orders = Order.objects.filter(order_date__date=target_date).exclude(order_status='ERROR').prefetch_related('items__product')
    
    orders_json = []
    for order in orders:
        items = [{'product_name': item.product.name, 'quantity': item.quantity} for item in order.items.all()]
        orders_json.append({'id': order.id, 'items': items})
        
    context = {
        'page_title': f'{date_str} 성공 주문 목록',
        'orders': orders,
        'list_type': 'success',
        'orders_json': orders_json,
    }
    return render(request, 'orders/order_list_result.html', context)

@login_required
def order_list_error_view(request, date_str):
    """
    선택한 날짜의 '오류' 주문 목록을 보여주는 뷰
    """
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    processed_errors = []

    db_error_orders = Order.objects.filter(order_date__date=target_date, order_status='ERROR')
    for order in db_error_orders:
        error_details = {}
        try:
            error_details = json.loads(order.error_message)
        except (json.JSONDecodeError, TypeError):
            pass
        
        original_data = error_details.get('original_data', {})
        processed_errors.append({
            'is_db': True,
            'unique_id': f"db-{order.id}",
            'id': order.id,
            'order_no': order.order_no,
            'recipient_name': order.recipient_name,
            'shipper_name': order.shipper.name if order.shipper else original_data.get('shipper_name', ''),
            'product_identifier': original_data.get('product_identifier', ''),
            'channel_name': order.channel.name if order.channel else original_data.get('channel_name', ''),
            'quantity': original_data.get('quantity', ''),
            'recipient_phone': order.recipient_phone,
            'address': order.address,
            'error_message': error_details.get('error_message', order.error_message or '알 수 없는 오류'),
            'error_fields': error_details.get('error_fields', []),
        })

    temp_errors = request.session.pop('temp_errors', [])
    for error in temp_errors:
        original_data = error.get('original_data', {})
        processed_errors.append({
            'is_db': False,
            'unique_id': f"session-{error.get('row_idx')}",
            'row_idx': error.get('row_idx'),
            'order_no': original_data.get('order_no', ''),
            'recipient_name': original_data.get('recipient_name', ''),
            'shipper_name': original_data.get('shipper_name', ''),
            'product_identifier': original_data.get('product_identifier', ''),
            'channel_name': original_data.get('channel_name', ''),
            'quantity': original_data.get('quantity', ''),
            'recipient_phone': original_data.get('recipient_phone', ''),
            'address': original_data.get('address', ''),
            'error_message': error.get('error_message', '알 수 없는 오류'),
            'error_fields': error.get('error_fields', []),
        })

    context = {
        'page_title': f'{date_str} 오류 주문 목록', 
        'orders': processed_errors,
        'list_type': 'error',
    }
    return render(request, 'orders/order_list_result.html', context)

@login_required
def order_update_view(request, order_pk):
    """
    오류 주문 상세 수정 페이지 뷰
    """
    order = get_object_or_404(Order, pk=order_pk, order_status='ERROR')
    if request.method == 'POST':
        form = OrderUpdateForm(request.POST, instance=order)
        if form.is_valid():
            updated_order = form.save(commit=False)
            updated_order.error_message = ""
            updated_order.order_status = 'PENDING'
            updated_order.save()
            messages.success(request, f"주문({order.order_no})이 성공적으로 수정되었습니다.")
            date_str = order.order_date.strftime('%Y-%m-%d')
            return redirect('orders:list_error', date_str=date_str)
    else:
        try:
            error_details = json.loads(order.error_message)
            initial_data = error_details.get('original_data', {})
            initial_data.update({ 'recipient_name': order.recipient_name, 'recipient_phone': order.recipient_phone, 'address': order.address })
            form = OrderUpdateForm(initial=initial_data)
        except (json.JSONDecodeError, TypeError):
            form = OrderUpdateForm(instance=order)
            
    context = { 'page_title': '오류 주문 수정', 'form': form, 'order': order }
    return render(request, 'orders/order_update_form.html', context)


@login_required
@require_POST
@transaction.atomic # [추가] 데이터베이스 트랜잭션 적용
def order_invoice_view(request):
    """
    송장 출력 및 자동 출고 처리 뷰
    """
    order_ids_str = request.POST.get('order_ids', '')
    if not order_ids_str:
        return HttpResponse("출력할 주문이 선택되지 않았습니다.", status=400)
    
    order_ids = [int(id) for id in order_ids_str.split(',')]
    # [수정] 출고 처리가 아직 안된 주문만 대상으로 함
    orders = Order.objects.filter(
        id__in=order_ids, 
        order_status__in=['PENDING', 'PROCESSING']
    ).select_related('shipper__center').prefetch_related('items__product')
    
    if not orders:
        return HttpResponse("출력할 주문이 없거나 이미 처리된 주문입니다.", status=404)
        
    # --- [신규] 자동 출고 처리 로직 ---
    for order in orders:
        for item in order.items.all():
            product = item.product
            # 1. 재고 수량 확인
            if product.quantity < item.quantity:
                messages.error(request, f"재고 부족: '{product.name}'의 출고를 처리할 수 없습니다. (현재 재고: {product.quantity})")
                # 트랜잭션을 롤백하고 함수를 종료
                transaction.set_rollback(True)
                # 이전 페이지로 리디렉션
                return redirect(request.META.get('HTTP_REFERER', 'orders:manage'))

            # 2. 재고 수량 차감
            product.quantity = F('quantity') - item.quantity
            product.save()

            # 3. 출고 기록(StockMovement) 생성
            StockMovement.objects.create(
                product=product,
                movement_type='OUT',
                quantity=item.quantity,
                memo=f'주문 출고 ({order.order_no})'
            )
    # ------------------------------------

    # 송장 출력 시 주문 상태를 '출고완료'로 변경
    orders.update(order_status='SHIPPED')
    
    context = {'orders': orders}
    return render(request, 'orders/invoice_template.html', context)

# ... (이하 API 뷰들은 그대로 유지) ...
@login_required
@require_POST
@transaction.atomic
def process_orders_api(request):
    """
    업로드된 엑셀 파일을 처리하여 주문을 생성하는 API
    """
    excel_file = request.FILES.get('excel_file')
    handle_duplicates = request.POST.get('handle_duplicates')
    if not excel_file:
        return JsonResponse({'status': 'error', 'message': '엑셀 파일이 없습니다.'}, status=400)

    wb = openpyxl.load_workbook(excel_file, data_only=True)
    sheet = wb.active
    
    success_orders, error_orders = [], []
    processed_in_this_file = set()

    for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        if not any(row): continue
        order_data = {
            'order_no': str(row[0]).strip() if row[0] else None, 'shipper_name': str(row[1]).strip() if row[1] else None,
            'channel_name': str(row[2]).strip() if row[2] else None, 'recipient_name': str(row[3]).strip() if row[3] else None,
            'recipient_phone': str(row[4]).strip() if row[4] else '', 'address': str(row[5]).strip() if row[5] else '',
            'product_identifier': str(row[6]).strip() if row[6] else None, 'quantity': int(row[7]) if row[7] and str(row[7]).isdigit() else 0,
        }
        
        errors, error_fields = [], []
        shipper = None

        try:
            if not order_data['shipper_name']: errors.append("화주사 정보 누락"); error_fields.append('shipper_name')
            else:
                try: shipper = Shipper.objects.get(name=order_data['shipper_name'])
                except Shipper.DoesNotExist: errors.append("미등록 화주사"); error_fields.append('shipper_name')

            if not order_data['product_identifier']: errors.append("상품 정보 누락"); error_fields.append('product_identifier')
            elif shipper and not Product.objects.filter(Q(barcode=order_data['product_identifier']) | Q(name=order_data['product_identifier']), shipper=shipper).exists():
                errors.append("미등록 상품"); error_fields.append('product_identifier')
            
            if not order_data['quantity'] or order_data['quantity'] <= 0: errors.append("수량 오류"); error_fields.append('quantity')
            if not order_data['channel_name']: errors.append("판매채널 누락"); error_fields.append('channel_name')
            if errors: raise ValueError(", ".join(sorted(list(set(errors)))))

            if handle_duplicates != 'yes':
                if Order.objects.filter(shipper=shipper, recipient_name=order_data['recipient_name'], address=order_data['address'], recipient_phone=order_data['recipient_phone']).exists(): continue
                file_dup_key = (order_data['shipper_name'], order_data['recipient_name'], order_data['address'], order_data['recipient_phone'])
                if file_dup_key in processed_in_this_file: continue
                processed_in_this_file.add(file_dup_key)

            channel, _ = SalesChannel.objects.get_or_create(name=order_data['channel_name'])
            product = Product.objects.get(Q(barcode=order_data['product_identifier']) | Q(name=order_data['product_identifier']), shipper=shipper)
            
            order = Order.objects.create(
                order_no=order_data['order_no'], shipper=shipper, channel=channel,
                recipient_name=order_data['recipient_name'], recipient_phone=order_data['recipient_phone'],
                address=order_data['address'], order_date=datetime.now(), order_status='PENDING'
            )
            OrderItem.objects.create(order=order, product=product, quantity=order_data['quantity'])
            success_orders.append(order)

        except Exception as e:
            error_packet = {
                'row_idx': row_idx, 'error_message': str(e),
                'error_fields': sorted(list(set(error_fields))), 'original_data': order_data
            }
            error_orders.append(error_packet)

    messages.success(request, f"엑셀 처리가 완료되었습니다. 성공: {len(success_orders)}건, 실패: {len(error_orders)}건")
    request.session['temp_errors'] = error_orders
    today_str = date.today().strftime('%Y-%m-%d')
    return JsonResponse({'status': 'success', 'redirect_url': reverse('orders:manage') + f'?date={today_str}'})

@login_required
@require_POST
@transaction.atomic
def batch_retry_error_api(request):
    """
    오류 목록 페이지에서 인라인 수정 후 일괄 재시도하는 API
    """
    all_items_data = json.loads(request.body)
    results = []
    for item_data in all_items_data:
        order_data = item_data.get('data', {})
        unique_id = item_data.get('unique_id')
        errors, error_fields = [], []; shipper = None
        try:
            if not order_data.get('shipper_name'): errors.append("화주사 정보 누락"); error_fields.append('shipper_name')
            else:
                try: shipper = Shipper.objects.get(name=order_data['shipper_name'])
                except Shipper.DoesNotExist: errors.append("미등록 화주사"); error_fields.append('shipper_name')
            
            if not order_data.get('product_identifier'): errors.append("상품 정보 누락"); error_fields.append('product_identifier')
            elif shipper and not Product.objects.filter(Q(barcode=order_data['product_identifier']) | Q(name=order_data['product_identifier']), shipper=shipper).exists():
                errors.append("미등록 상품"); error_fields.append('product_identifier')

            if not order_data.get('quantity') or int(order_data.get('quantity', 0)) <= 0: errors.append("수량 오류"); error_fields.append('quantity')
            if errors: raise ValueError(", ".join(sorted(list(set(errors)))))
            
            channel, _ = SalesChannel.objects.get_or_create(name=order_data['channel_name'])
            product = Product.objects.get(Q(barcode=order_data['product_identifier']) | Q(name=order_data['product_identifier']), shipper=shipper)
            
            new_order = Order.objects.create(
                order_no=order_data.get('order_no') or None, shipper=shipper, channel=channel,
                recipient_name=order_data['recipient_name'], recipient_phone=order_data['recipient_phone'],
                address=order_data['address'], order_date=datetime.now(), order_status='PENDING'
            )
            OrderItem.objects.create(order=new_order, product=product, quantity=order_data['quantity'])
            
            id_type, id_value = unique_id.split('-')
            if id_type == 'db': Order.objects.filter(id=id_value).delete()
            elif id_type == 'session' and 'temp_errors' in request.session:
                request.session['temp_errors'] = [e for e in request.session['temp_errors'] if e.get('row_idx') != int(id_value)]
                request.session.modified = True
            
            results.append({'unique_id': unique_id, 'status': 'success'})

        except Exception as e:
            results.append({ 'unique_id': unique_id, 'status': 'error', 'error_message': str(e), 'error_fields': sorted(list(set(error_fields))) })
            
    return JsonResponse({'results': results})

@login_required
def product_autocomplete_api(request):
    """
    오류 수정 시 상품명/바코드 자동완성을 위한 API
    """
    shipper_name = request.GET.get('shipper_name'); term = request.GET.get('term')
    if not shipper_name or not term: return JsonResponse([], safe=False)
    products = Product.objects.filter(Q(name__icontains=term) | Q(barcode__icontains=term), shipper__name=shipper_name).values_list('name', flat=True)[:10]
    return JsonResponse(list(products), safe=False)

@login_required
def order_chart_data_api(request):
    """
    홈 대시보드의 일별 주문 추이 차트 데이터를 제공하는 API
    """
    start_str = request.GET.get('start'); end_str = request.GET.get('end')
    try: start_date, end_date = datetime.strptime(start_str, '%Y-%m-%d').date(), datetime.strptime(end_str, '%Y-%m-%d').date()
    except (ValueError, TypeError): end_date, start_date = date.today(), date.today() - timedelta(days=6)
    
    labels = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]
    status_map = { 'PENDING': '주문접수', 'PROCESSING': '처리중', 'ERROR': '오류' }
    
    orders = Order.objects.filter(order_date__date__range=[start_date, end_date], order_status__in=status_map.keys()).annotate(date=TruncDate('order_date')).values('date', 'order_status').annotate(count=Count('id')).order_by('date')
    
    daily_counts = {label: {status: 0 for status in status_map} for label in labels}
    for order in orders:
        date_str = order['date'].strftime('%Y-%m-%d')
        if date_str in daily_counts: daily_counts[date_str][order['order_status']] = order['count']
            
    colors = { 'PENDING': 'rgba(54, 162, 235, 0.7)', 'PROCESSING': 'rgba(255, 159, 64, 0.7)', 'ERROR': 'rgba(255, 99, 132, 0.7)' }
    datasets = []
    for code, name in status_map.items():
        data = [daily_counts[label][code] for label in labels]
        if any(d > 0 for d in data):
            datasets.append({ 'label': name, 'data': data, 'borderColor': colors.get(code), 'backgroundColor': colors.get(code), 'fill': False, 'tension': 0.1 })
            
    return JsonResponse({'labels': labels, 'datasets': datasets})

@login_required
def channel_order_chart_data_api(request):
    """
    주문 관리 페이지의 채널별 주문량 원형 차트 데이터를 제공하는 API
    """
    date_str = request.GET.get('date')
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    
    orders_for_date = Order.objects.filter(order_date__date=target_date)
    channel_counts = SalesChannel.objects.filter(order__in=orders_for_date).annotate(order_count=Count('order')).values('name', 'order_count')
    
    labels = [data['name'] for data in channel_counts]
    data = [data['order_count'] for data in channel_counts]
    return JsonResponse({'labels': labels, 'data': data})