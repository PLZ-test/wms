from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.db.models import Sum, F, Count, Q
from datetime import datetime, date, timedelta
from django.db.models.functions import TruncDate
from django.db import transaction
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .models import Center, Shipper, Courier, Product, User, Order, OrderItem, SalesChannel, StockMovement
from .forms import (
    CenterForm, ShipperForm, CourierForm, ProductForm, StockIOForm,
    StockUpdateForm, UserUpdateForm, CustomUserCreationForm, OrderUpdateForm
)
import openpyxl
from django.views.decorators.http import require_POST
import json


# ----------------------------------------
# 송장 출력 뷰
# ----------------------------------------
@login_required
@require_POST
def order_invoice_view(request):
    # 요청 본문에서 'order_ids'를 가져옴
    order_ids_str = request.POST.get('order_ids', '')
    if not order_ids_str:
        return HttpResponse("출력할 주문이 선택되지 않았습니다.", status=400)
    
    # 쉼표로 구분된 ID 문자열을 정수 리스트로 변환
    order_ids = [int(id) for id in order_ids_str.split(',')]
    # 해당 ID의 주문들을 조회 (관련 모델 prefetch로 최적화)
    orders = Order.objects.filter(id__in=order_ids).select_related('shipper__center').prefetch_related('items__product')
    if not orders:
        return HttpResponse("유효한 주문을 찾을 수 없습니다.", status=404)
    
    # 선택된 주문들의 상태를 'SHIPPED'(출고완료)로 일괄 업데이트
    Order.objects.filter(id__in=order_ids).update(order_status='SHIPPED')
    
    context = {'orders': orders}
    return render(request, 'wms_app/invoice_template.html', context)

# ----------------------------------------
# API 뷰
# ----------------------------------------

@login_required
@require_POST
def check_duplicates_api(request):
    """엑셀 파일 업로드 시 DB에 동일한 주문 정보가 있는지 사전 확인하는 API"""
    excel_file = request.FILES.get('excel_file')
    if not excel_file:
        return JsonResponse({'error': '엑셀 파일이 없습니다.'}, status=400)
    try:
        wb = openpyxl.load_workbook(excel_file, data_only=True)
        sheet = wb.active
        duplicate_count = 0
        # 엑셀의 2번째 행부터 순회하며 데이터 확인
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not any(row): continue
            # 중복 검사를 위한 핵심 필드 추출
            shipper_name = str(row[1]).strip() if row[1] else None
            recipient_name = str(row[3]).strip() if row[3] else None
            recipient_phone = str(row[4]).strip() if row[4] else None
            address = str(row[5]).strip() if row[5] else None
            
            # 필수 필드가 하나라도 없으면 건너뜀
            if not all([shipper_name, recipient_name, recipient_phone, address]):
                continue
            
            # 동일한 화주사, 수취인명, 주소, 연락처를 가진 주문이 존재하는지 확인
            if Order.objects.filter(shipper__name=shipper_name, recipient_name=recipient_name, address=address, recipient_phone=recipient_phone).exists():
                duplicate_count += 1
                
        return JsonResponse({'has_duplicates': duplicate_count > 0, 'duplicate_count': duplicate_count})
    except Exception as e:
        return JsonResponse({'error': f'파일 검사 중 오류 발생: {str(e)}'}, status=500)

@login_required
@require_POST
@transaction.atomic
def process_orders_api(request):
    """엑셀 파일을 받아 주문을 생성하고, 오류 발생 시 DB에 영구 기록하는 API"""
    excel_file = request.FILES.get('excel_file')
    handle_duplicates = request.POST.get('handle_duplicates')
    if not excel_file:
        return JsonResponse({'status': 'error', 'message': '엑셀 파일이 없습니다.'}, status=400)

    wb = openpyxl.load_workbook(excel_file, data_only=True)
    sheet = wb.active
    
    current_success_orders = []
    current_error_orders = []
    processed_in_this_file = set() # 파일 내 중복 처리를 위한 집합

    for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        if not any(row): continue
        # 엑셀 행 데이터를 딕셔너리로 정리
        order_data = {
            'order_no': str(row[0]).strip() if row[0] else None, 'shipper_name': str(row[1]).strip() if row[1] else None,
            'channel_name': str(row[2]).strip() if row[2] else None, 'recipient_name': str(row[3]).strip() if row[3] else None,
            'recipient_phone': str(row[4]).strip() if row[4] else '', 'address': str(row[5]).strip() if row[5] else '',
            'product_identifier': str(row[6]).strip() if row[6] else None, 'quantity': int(row[7]) if row[7] and str(row[7]).isdigit() else 0,
        }
        error_info = {} # 오류 발생 시 상세 정보를 담을 딕셔너리
        try:
            # 필수 정보 유효성 검사
            if not all([order_data['shipper_name'], order_data['channel_name'], order_data['recipient_name'], order_data['recipient_phone'], order_data['address'], order_data['product_identifier'], order_data['quantity'] > 0]):
                error_info = {'error_field': 'multiple', 'error_value': ''}
                raise ValueError('필수 정보(화주사,채널,수취인정보,상품,수량)가 누락/잘못되었습니다.')

            shipper = Shipper.objects.get(name=order_data['shipper_name'])
            
            # DB에 이미 존재하는 주문인지 확인
            is_duplicate_db = Order.objects.filter(shipper=shipper, recipient_name=order_data['recipient_name'], address=order_data['address'], recipient_phone=order_data['recipient_phone']).exists()
            
            if is_duplicate_db:
                if handle_duplicates == 'yes': # 중복 허용 옵션 선택 시
                    order_data['order_no'] = None # 주문번호를 비워 새 주문으로 생성
                else: # 중복 무시 옵션 선택 시
                    continue
            
            # 파일 내 중복 데이터 처리 (중복 무시 옵션 선택 시)
            if handle_duplicates == 'no':
                file_duplicate_key = (order_data['shipper_name'], order_data['recipient_name'], order_data['address'], order_data['recipient_phone'])
                if file_duplicate_key in processed_in_this_file:
                    continue
                processed_in_this_file.add(file_duplicate_key)

            channel, _ = SalesChannel.objects.get_or_create(name=order_data['channel_name'])
            product = Product.objects.filter(Q(barcode=order_data['product_identifier']) | Q(name=order_data['product_identifier']), shipper=shipper).first()
            if not product:
                error_info = {'error_field': 'product_identifier', 'error_value': order_data['product_identifier']}
                raise Product.DoesNotExist(f"상품 '{order_data['product_identifier']}'을(를) 찾을 수 없습니다.")

            # 정상 주문 생성
            order = Order.objects.create(
                order_no=order_data['order_no'], shipper=shipper, channel=channel,
                recipient_name=order_data['recipient_name'], recipient_phone=order_data['recipient_phone'],
                address=order_data['address'], order_date=datetime.now(), order_status='PENDING'
            )
            OrderItem.objects.create(order=order, product=product, quantity=order_data['quantity'])
            current_success_orders.append(order)
            
        except Exception as e:
            # [핵심 수정] 오류 발생 시, 상세 오류 정보를 포함하여 DB에 'ERROR' 상태로 영구 저장
            error_data_packet = {
                'row_idx': row_idx,
                'error_message': str(e),
                'error_field': error_info.get('error_field', 'unknown'),
                'error_value': error_info.get('error_value', ''),
                'original_data': order_data,
            }
            try:
                # 오류 저장을 위해 최소한의 정보(화주사, 채널)라도 가져오려 시도
                shipper = Shipper.objects.filter(name=order_data['shipper_name']).first()
                channel, _ = SalesChannel.objects.get_or_create(name=order_data['channel_name'])
                # 오류 주문 객체를 생성하여 DB에 저장
                error_order = Order.objects.create(
                    order_no=order_data['order_no'] or f"NO_ID_ERROR-{row_idx}",
                    shipper=shipper, channel=channel,
                    recipient_name=order_data['recipient_name'], recipient_phone=order_data['recipient_phone'],
                    address=order_data['address'], order_date=datetime.now(), 
                    order_status='ERROR', error_message=json.dumps(error_data_packet) # 상세 오류 정보를 JSON 문자열로 저장
                )
                current_error_orders.append(error_order)
            except Exception:
                # 위 과정조차 실패하면 (e.g., DB 제약조건 위반 등) 최후의 수단으로 임시 세션에 오류 기록
                current_error_orders.append(error_data_packet)

    messages.success(request, f"엑셀 처리가 완료되었습니다. 성공: {len(current_success_orders)}건, 실패: {len(current_error_orders)}건")
    # DB 저장에 실패한 건만 세션에 임시 저장
    request.session['temp_errors'] = [e for e in current_error_orders if isinstance(e, dict)]
    today_str = date.today().strftime('%Y-%m-%d')
    return JsonResponse({'status': 'success', 'redirect_url': reverse('order_manage') + f'?date={today_str}'})

@login_required
@require_POST
@transaction.atomic
def retry_error_order_api(request):
    """오류 목록에서 사용자가 수정한 데이터를 받아 주문을 재처리하는 API"""
    data = json.loads(request.body)
    order_data = data.get('original_data', {})
    
    try:
        shipper = Shipper.objects.get(name=order_data['shipper_name'])
        channel, _ = SalesChannel.objects.get_or_create(name=order_data['channel_name'])
        product = Product.objects.filter(Q(barcode=order_data['product_identifier']) | Q(name=order_data['product_identifier']), shipper=shipper).first()
        
        if not product:
            raise Product.DoesNotExist(f"상품 '{order_data['product_identifier']}'을(를) 찾을 수 없습니다.")

        # 새로운 주문 생성
        new_order = Order.objects.create(
            order_no=order_data['order_no'] or None, shipper=shipper, channel=channel,
            recipient_name=order_data['recipient_name'], recipient_phone=order_data['recipient_phone'],
            address=order_data['address'], order_date=datetime.now(), order_status='PENDING'
        )
        OrderItem.objects.create(order=new_order, product=product, quantity=order_data['quantity'])

        # 재처리에 성공한 임시 오류 데이터를 세션에서 제거
        if 'temp_errors' in request.session:
            row_idx_to_remove = data.get('row_idx')
            request.session['temp_errors'] = [e for e in request.session['temp_errors'] if e.get('row_idx') != row_idx_to_remove]
            request.session.modified = True

        return JsonResponse({'status': 'success', 'order_id': new_order.id})

    except Exception as e:
        # 재시도 실패 시, 어떤 필드에서 오류가 발생했는지 구체적인 정보 반환
        error_field = 'unknown'
        error_value = ''
        if isinstance(e, Shipper.DoesNotExist):
            error_field = 'shipper_name'
            error_value = order_data['shipper_name']
        elif isinstance(e, Product.DoesNotExist):
            error_field = 'product_identifier'
            error_value = order_data['product_identifier']
            
        new_error_info = {
            'error_message': str(e),
            'error_field': error_field,
            'error_value': error_value,
        }
        return JsonResponse({'status': 'error', 'error_info': new_error_info})


@login_required
def channel_order_chart_data(request):
    """주문 관리 페이지의 판매 채널별 주문 현황 파이 차트 데이터 API"""
    date_str = request.GET.get('date')
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    orders_for_date = Order.objects.filter(order_date__date=target_date)
    channel_counts = SalesChannel.objects.filter(order__in=orders_for_date).annotate(order_count=Count('order')).values('name', 'order_count')
    labels = [data['name'] for data in channel_counts]
    data = [data['order_count'] for data in channel_counts]
    return JsonResponse({'labels': labels, 'data': data})


@login_required
def order_list_api(request):
    """주문 목록을 필터링하여 JSON으로 반환하는 API (현재 사용되지 않을 수 있음)"""
    status = request.GET.get('status')
    orders = Order.objects.all()
    if status == 'success':
        orders = orders.exclude(order_status='ERROR')
    elif status == 'error':
        orders = orders.filter(order_status='ERROR')
    data = []
    for order in orders:
        items = [{'product_name': item.product.name, 'quantity': item.quantity} for item in order.items.all()]
        data.append({
            'id': order.id, 'order_no': order.order_no,
            'shipper': order.shipper.name if order.shipper else '-',
            'channel': order.channel.name if order.channel else '-',
            'recipient': order.recipient_name, 'status': order.get_order_status_display(),
            'error_message': order.error_message, 'items': items,
        })
    return JsonResponse({'orders': data})

def check_username(request):
    """회원가입 시 사용자 이름(ID) 중복을 확인하는 API"""
    username = request.GET.get('username', None)
    is_taken = User.objects.filter(username__iexact=username).exists()
    data = {'is_available': not is_taken}
    return JsonResponse(data)

@login_required
def order_chart_data(request):
    """대시보드의 기간별 주문 현황 라인 차트 데이터 API"""
    start_date_str = request.GET.get('start')
    end_date_str = request.GET.get('end')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        # 날짜 파라미터가 없으면 기본값으로 최근 7일 설정
        end_date = date.today()
        start_date = end_date - timedelta(days=6)

    labels = []
    current_date = start_date
    while current_date <= end_date:
        labels.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
        
    status_map = { 'PENDING': '주문접수', 'PROCESSING': '처리중', 'ERROR': '오류' }

    # 지정된 기간과 상태의 주문들을 날짜와 상태별로 그룹화하여 카운트
    orders = Order.objects.filter(
            order_date__date__range=[start_date, end_date],
            order_status__in=status_map.keys()
        ).annotate(date=TruncDate('order_date')) \
         .values('date', 'order_status') \
         .annotate(count=Count('id')) \
         .order_by('date')

    daily_counts = {label: {status: 0 for status in status_map} for label in labels}
    for order in orders:
        date_str = order['date'].strftime('%Y-%m-%d')
        if date_str in daily_counts:
            daily_counts[date_str][order['order_status']] = order['count']

    status_colors = { 'PENDING': 'rgba(54, 162, 235, 0.7)', 'PROCESSING': 'rgba(255, 159, 64, 0.7)', 'ERROR': 'rgba(255, 99, 132, 0.7)' }

    final_datasets = []
    for status_code, status_name in status_map.items():
        data = [daily_counts[label][status_code] for label in labels]
        if any(d > 0 for d in data): # 데이터가 있는 상태만 차트에 표시
            final_datasets.append({
                'label': status_name, 'data': data,
                'borderColor': status_colors.get(status_code, 'rgba(0, 0, 0, 0.7)'),
                'backgroundColor': status_colors.get(status_code, 'rgba(0, 0, 0, 0.7)'),
                'fill': False, 'tension': 0.1
            })
    return JsonResponse({'labels': labels, 'datasets': final_datasets})

@login_required
def delivery_chart_data(request):
    """대시보드의 배송 현황 도넛 차트 데이터 API (현재는 임시 데이터 사용)"""
    data = {'집하완료': 12, '배송중': 8, '배송완료': 30}
    return JsonResponse(data)

# ----------------------------------------
# 인증 뷰
# ----------------------------------------
def wms_logout_view(request):
    logout(request)
    return redirect('login')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    def form_invalid(self, form):
        messages.error(self.request, '아이디 또는 비밀번호가 올바르지 않습니다.')
        return super().form_invalid(form)
    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
            messages.error(self.request, '아직 승인되지 않은 계정입니다. 관리자에게 문의하세요.')
            return self.form_invalid(form)
        return super().form_valid(form)

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('signup_done')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def signup_done_view(request):
    return render(request, 'registration/signup_done.html')

# ----------------------------------------
# 페이지 렌더링 뷰
# ----------------------------------------
@login_required
def dashboard(request):
    """대시보드 페이지 뷰"""
    context = {'page_title': '홈', 'active_menu': 'dashboard'}
    return render(request, 'wms_app/order_list_page.html', context)

@login_required
def order_manage(request):
    """주문 관리 메인 페이지 뷰"""
    date_str = request.GET.get('date')
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    
    orders_for_date = Order.objects.filter(order_date__date=selected_date)
    
    # DB에 저장된 주문 수 계산
    total_count = orders_for_date.count()
    success_count = orders_for_date.exclude(order_status='ERROR').count()
    error_count_db = orders_for_date.filter(order_status='ERROR').count()
    
    # 세션에 임시 저장된 오류 건수 계산 (DB 저장 실패 건)
    temp_errors_count = len(request.session.get('temp_errors', []))
    total_count += temp_errors_count
    error_count = error_count_db + temp_errors_count

    daily_stats = {
        'total_count': total_count, 'success_count': success_count, 'error_count': error_count,
        'success_rate': (success_count / total_count * 100) if total_count > 0 else 0,
        'error_rate': (error_count / total_count * 100) if total_count > 0 else 0,
    }

    context = {
        'page_title': '주문 관리', 'active_menu': 'orders',
        'selected_date': selected_date.strftime('%Y-%m-%d'),
        'daily_stats': daily_stats,
    }
    return render(request, 'wms_app/order_manage.html', context)

@login_required
def order_list_success(request, date_str):
    """성공 주문 목록 페이지 뷰"""
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    orders = Order.objects.filter(order_date__date=target_date).exclude(order_status='ERROR').prefetch_related('items__product')
    
    # JavaScript에서 주문별 상품 내역을 확인하기 위한 JSON 데이터 생성
    orders_json = []
    for order in orders:
        items = [{'product_name': item.product.name, 'quantity': item.quantity} for item in order.items.all()]
        orders_json.append({'id': order.id, 'items': items})

    context = {
        'page_title': f'{date_str} 성공 주문 목록', 'orders': orders,
        'list_type': 'success', 'orders_json': orders_json,
    }
    return render(request, 'wms_app/order_list_result.html', context)

@login_required
def order_list_error(request, date_str):
    """오류 주문 목록 페이지 뷰"""
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    db_errors = []
    # DB에 저장된 오류 주문들을 조회
    for order in Order.objects.filter(order_date__date=target_date, order_status='ERROR'):
        try:
            # [핵심 수정] error_message 필드의 JSON 문자열을 파싱하여 상세 정보 추출
            error_details = json.loads(order.error_message)
            order.original_data = error_details.get('original_data', {})
            order.error_message = error_details.get('error_message', order.error_message)
            order.error_field = error_details.get('error_field', 'unknown')
            order.error_value = error_details.get('error_value', '')
        except (json.JSONDecodeError, TypeError):
            # 파싱 실패 시 (단순 문자열로 저장된 경우 등) 기본값 설정
            order.original_data = {}
            order.error_field = 'unknown'
            order.error_value = ''
        db_errors.append(order)

    # 세션에서 임시 오류 데이터 가져오기 (가져온 후 세션에서 제거)
    temp_errors = request.session.pop('temp_errors', [])

    all_errors = db_errors + temp_errors
    
    orders_json = []
    for order in db_errors:
        if hasattr(order, 'items') and order.items.exists():
            items = [{'product_name': item.product.name, 'quantity': item.quantity} for item in order.items.all()]
            orders_json.append({'id': order.id, 'items': items})

    context = {
        'page_title': f'{date_str} 오류 주문 목록', 'orders': all_errors,
        'list_type': 'error', 'orders_json': json.dumps(orders_json),
    }
    return render(request, 'wms_app/order_list_result.html', context)

@login_required
def order_update_view(request, order_pk):
    """오류 주문 수정 페이지 뷰"""
    order = get_object_or_404(Order, pk=order_pk)
    if request.method == 'POST':
        form = OrderUpdateForm(request.POST, instance=order)
        if form.is_valid():
            # TODO: 저장 전, 수정된 데이터로 주문을 다시 생성할 수 있는지 재검증하는 로직 추가 가능
            updated_order = form.save(commit=False)
            updated_order.error_message = "" # 오류 메시지 초기화
            updated_order.order_status = 'PENDING' # 상태를 '주문접수'로 변경
            updated_order.save()
            messages.success(request, f"주문({order.order_no})이 성공적으로 수정되었습니다.")
            date_str = order.order_date.strftime('%Y-%m-%d')
            return redirect('order_list_error', date_str=date_str)
    else:
        # [핵심 수정] GET 요청 시, DB에 저장된 오류 정보(JSON)를 파싱하여 폼에 초기값으로 전달
        try:
            error_details = json.loads(order.error_message)
            initial_data = error_details.get('original_data', {})
            # DB의 Order 객체 정보로 일부 데이터 덮어쓰기 (가장 최신 정보 유지)
            initial_data.update({
                'shipper': order.shipper, 'channel': order.channel, 'order_no': order.order_no,
                'recipient_name': order.recipient_name, 'recipient_phone': order.recipient_phone,
                'address': order.address,
            })
            form = OrderUpdateForm(initial=initial_data)
        except (json.JSONDecodeError, TypeError):
            # JSON 파싱 실패 시, 기존 방식대로 Order 인스턴스 정보로 폼 생성
            form = OrderUpdateForm(instance=order)

    context = { 'page_title': '오류 주문 수정', 'form': form, 'order': order }
    return render(request, 'wms_app/order_update_form.html', context)
    
@login_required
def management_dashboard(request):
    """통합 관리 대시보드 뷰"""
    context = {
        'page_title': '통합 관리', 'active_menu': 'management',
        'shipper_count': Shipper.objects.count(), 'product_count': Product.objects.count(),
        'center_count': Center.objects.count(), 'courier_count': Courier.objects.count(),
    }
    return render(request, 'wms_app/management_dashboard.html', context)

@login_required
def stock_manage(request):
    """재고 관리 페이지 뷰"""
    queryset = Product.objects.select_related('shipper__center').all()
    # 세션에 저장된 필터 값으로 쿼리셋 필터링
    selected_center = request.session.get('selected_center')
    selected_shipper = request.session.get('selected_shipper')
    if selected_center:
        queryset = queryset.filter(shipper__center__name=selected_center)
    if selected_shipper:
        queryset = queryset.filter(shipper__name=selected_shipper)
    context = {
        'page_title': '재고관리', 'object_list': queryset,
        'columns': [
            {'header': '상품명', 'key': 'name'}, {'header': '크기(cm)', 'is_size': True},
            {'header': '재고', 'key': 'quantity'}, {'header': '바코드', 'key': 'barcode'},
            {'header': '화주사명', 'key': 'shipper'},
        ], 'active_menu': 'management', 'update_url_name': 'stock_update',
    }
    return render(request, 'wms_app/generic_list.html', context)

@login_required
@transaction.atomic
def stock_io_view(request):
    """재고 입출고 처리 뷰"""
    if request.method == 'POST':
        form_data = request.POST.copy()
        form_data['product'] = request.POST.get('product')
        form = StockIOForm(form_data)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            memo = form.cleaned_data['memo']
            io_type = request.POST.get('io_type') # 'in' or 'out'
            
            if io_type == 'in': # 입고
                product.quantity = F('quantity') + quantity
                movement_type = 'IN'
            elif io_type == 'out': # 출고
                product.refresh_from_db() # 동시성 문제 방지를 위해 최신 재고 다시 로드
                if product.quantity < quantity:
                    return HttpResponseBadRequest("재고가 부족합니다.")
                product.quantity = F('quantity') - quantity
                movement_type = 'OUT'
            
            product.save()
            # 재고 변동 이력(StockMovement) 생성
            StockMovement.objects.create(product=product, movement_type=movement_type, quantity=quantity, memo=memo)
            return redirect('stock_io')
            
    products = Product.objects.select_related('shipper__center').all()
    selected_center = request.session.get('selected_center')
    selected_shipper = request.session.get('selected_shipper')
    if selected_center:
        products = products.filter(shipper__center__name=selected_center)
    if selected_shipper:
        products = products.filter(shipper__name=selected_shipper)
    context = {'page_title': '재고 입출고', 'products': products, 'active_menu': 'inout'}
    return render(request, 'wms_app/stock_io.html', context)

@login_required
def stock_update(request, pk):
    """재고 수량 직접 수정 뷰"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('stock_manage')
    else:
        form = StockUpdateForm(instance=product)
    context = { 'form': form, 'product': product, 'page_title': '재고 수량 수정', 'active_menu': 'management' }
    return render(request, 'wms_app/stock_update_form.html', context)

@login_required
def stock_movement_history(request):
    """재고 입출고 기록 조회 뷰"""
    movements = StockMovement.objects.select_related('product__shipper').order_by('-timestamp')
    context = { 'page_title': '입출고 기록', 'movements': movements, 'active_menu': 'inout' }
    return render(request, 'wms_app/stock_history.html', context)

@login_required
def user_manage(request):
    """사용자 관리 목록 뷰"""
    user_list = User.objects.filter(is_superuser=False)
    context = { 'page_title': '사용자 관리', 'active_menu': 'management', 'user_list': user_list, }
    return render(request, 'wms_app/user_list.html', context)

@login_required
def user_update(request, pk):
    """사용자 정보 수정 뷰"""
    user_instance = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_instance)
        if form.is_valid():
            form.save()
            return redirect('user_manage')
    else:
        form = UserUpdateForm(instance=user_instance)
    context = { 'form': form, 'target_user': user_instance, 'page_title': '사용자 역할 및 소속 수정', 'active_menu': 'management' }
    return render(request, 'wms_app/user_form.html', context)

# (이하 플레이스홀더 및 CBV 뷰들은 기능 확장 시 구현 예정)
@login_required
def order_manage_new(request):
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '주문 관리', 'active_menu': 'management'})

@login_required
def stock_in(request):
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '입고', 'active_menu': 'inout'})

@login_required
def stock_out(request):
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '출고', 'active_menu': 'inout'})

@login_required
def settlement_status(request):
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '정산 현황', 'active_menu': 'settlement'})

@login_required
def settlement_billing(request):
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '정산 청구내역', 'active_menu': 'settlement'})

@login_required
def settlement_config(request):
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '정산내역설정', 'active_menu': 'settlement'})

# --- Class Based Views for CRUD ---

class CenterListView(LoginRequiredMixin, ListView):
    model = Center
    template_name = 'wms_app/generic_list.html'
    context_object_name = 'object_list'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '센터 관리', 'columns': [{'header': '센터명', 'key': 'name'}, {'header': '주소', 'key': 'address'}],
            'create_url': reverse_lazy('center_create'), 'update_url_name': 'center_update', 'delete_url_name': 'center_delete',
            'active_menu': 'management'
        })
        return context

class CenterCreateView(LoginRequiredMixin, CreateView):
    model = Center
    form_class = CenterForm
    template_name = 'wms_app/generic_form.html'
    success_url = reverse_lazy('center_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '센터 등록'
        context['active_menu'] = 'management'
        return context

class CenterUpdateView(LoginRequiredMixin, UpdateView):
    model = Center
    form_class = CenterForm
    template_name = 'wms_app/generic_form.html'
    success_url = reverse_lazy('center_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '센터 편집'
        context['active_menu'] = 'management'
        return context

class CenterDeleteView(LoginRequiredMixin, DeleteView):
    model = Center
    success_url = reverse_lazy('center_list')

class ShipperListView(LoginRequiredMixin, ListView):
    model = Shipper
    template_name = 'wms_app/generic_list.html'
    context_object_name = 'object_list'
    def get_queryset(self):
        queryset = super().get_queryset().select_related('center')
        selected_center = self.request.session.get('selected_center')
        if selected_center:
            queryset = queryset.filter(center__name=selected_center)
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '화주사 관리', 'columns': [{'header': '화주사명', 'key': 'name'}, {'header': '담당자', 'key': 'contact'}, {'header': '소속 센터', 'key': 'center'}],
            'create_url': reverse_lazy('shipper_create'), 'update_url_name': 'shipper_update', 'delete_url_name': 'shipper_delete',
            'extra_actions': [{'label': '판매 상품', 'url_name': 'shipper_product_list', 'class': 'btn-info'}], 'active_menu': 'management'
        })
        return context

class ShipperCreateView(LoginRequiredMixin, CreateView):
    model = Shipper
    form_class = ShipperForm
    template_name = 'wms_app/generic_form.html'
    success_url = reverse_lazy('shipper_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '화주사 등록'
        context['active_menu'] = 'management'
        return context

class ShipperUpdateView(LoginRequiredMixin, UpdateView):
    model = Shipper
    form_class = ShipperForm
    template_name = 'wms_app/generic_form.html'
    success_url = reverse_lazy('shipper_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '화주사 편집'
        context['active_menu'] = 'management'
        return context

class ShipperDeleteView(LoginRequiredMixin, DeleteView):
    model = Shipper
    success_url = reverse_lazy('shipper_list')

class CourierListView(LoginRequiredMixin, ListView):
    model = Courier
    template_name = 'wms_app/generic_list.html'
    context_object_name = 'object_list'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '택배사 관리', 'columns': [{'header': '택배사명', 'key': 'name'}, {'header': '연락처', 'key': 'contact'}],
            'create_url': reverse_lazy('courier_create'), 'update_url_name': 'courier_update', 'delete_url_name': 'courier_delete',
            'active_menu': 'management'
        })
        return context

class CourierCreateView(LoginRequiredMixin, CreateView):
    model = Courier
    form_class = CourierForm
    template_name = 'wms_app/generic_form.html'
    success_url = reverse_lazy('courier_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '택배사 등록'
        context['active_menu'] = 'management'
        return context

class CourierUpdateView(LoginRequiredMixin, UpdateView):
    model = Courier
    form_class = CourierForm
    template_name = 'wms_app/generic_form.html'
    success_url = reverse_lazy('courier_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '택배사 편집'
        context['active_menu'] = 'management'
        return context

class CourierDeleteView(LoginRequiredMixin, DeleteView):
    model = Courier
    success_url = reverse_lazy('courier_list')

@login_required
def shipper_product_list(request, shipper_pk):
    """화주사별 판매 상품 목록 뷰"""
    shipper = get_object_or_404(Shipper, pk=shipper_pk)
    products = Product.objects.filter(shipper=shipper)
    context = { 'shipper': shipper, 'products': products, 'page_title': f'{shipper.name} 판매 상품', 'active_menu': 'management' }
    return render(request, 'wms_app/shipper_product_list.html', context)

@login_required
def shipper_product_create(request, shipper_pk):
    """화주사별 판매 상품 등록 뷰"""
    shipper = get_object_or_404(Shipper, pk=shipper_pk)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.shipper = shipper
            product.save()
            return redirect('shipper_product_list', shipper_pk=shipper.pk)
    else:
        form = ProductForm()
    context = { 'form': form, 'shipper': shipper, 'page_title': f'{shipper.name} 상품 등록', 'active_menu': 'management' }
    return render(request, 'wms_app/shipper_product_form.html', context)

@login_required
def shipper_product_update(request, pk):
    """화주사별 판매 상품 수정 뷰"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('shipper_product_list', shipper_pk=product.shipper.pk)
    else:
        form = ProductForm(instance=product)
    context = { 'form': form, 'page_title': '판매 상품 편집', 'active_menu': 'management' }
    return render(request, 'wms_app/shipper_product_form.html', context)

@login_required
def shipper_product_delete(request, pk):
    """화주사별 판매 상품 삭제 처리 뷰"""
    product = get_object_or_404(Product, pk=pk)
    shipper_pk = product.shipper.pk
    if request.method == 'POST':
        product.delete()
        return redirect('shipper_product_list', shipper_pk=shipper_pk)
    return HttpResponseBadRequest("잘못된 요청입니다.")

def filters(request):
    """(Context Processor용) 헤더 필터에 필요한 데이터를 제공하는 함수"""
    selected_center_name = request.session.get('selected_center', '')
    shippers = Shipper.objects.all()
    if selected_center_name:
        shippers = shippers.filter(center__name=selected_center_name)
    return {
        'centers': Center.objects.all(), 'shippers': shippers,
        'selected_center': selected_center_name, 'selected_shipper': request.session.get('selected_shipper', ''),
    }