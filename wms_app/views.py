# wms_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Sum, F, Count, Q
from datetime import datetime
from django.db import transaction
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .models import Center, Shipper, Courier, Product, Order, StockMovement, User, SalesChannel, OrderItem
from .forms import CenterForm, ShipperForm, CourierForm, ProductForm, StockIOForm, StockUpdateForm, UserUpdateForm, CustomUserCreationForm
import openpyxl

# ----------------------------------------
# API 뷰
# ----------------------------------------

@login_required
def order_list_api(request):
    """
    주문 목록 데이터를 JSON 형태로 반환하는 API 뷰입니다.
    JavaScript에서 이 API를 호출하여 주문 관리 페이지의 테이블을 동적으로 구성합니다.
    URL 파라미터(status)에 따라 '성공' 또는 '오류' 주문을 필터링합니다.
    """
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
            'id': order.id,
            'order_no': order.order_no,
            'shipper': order.shipper.name if order.shipper else '-',
            'channel': order.channel.name if order.channel else '-',
            'recipient': order.recipient_name,
            'status': order.get_order_status_display(),
            'error_message': order.error_message,
            'items': items,
        })
    return JsonResponse({'orders': data})

def check_username(request):
    """
    회원가입 시 사용자 아이디(username) 중복 여부를 실시간으로 확인하는 API 뷰입니다.
    """
    username = request.GET.get('username', None)
    is_taken = User.objects.filter(username__iexact=username).exists()
    data = {'is_available': not is_taken}
    return JsonResponse(data)

@login_required
def order_chart_data(request):
    """
    대시보드의 주문 현황 차트에 필요한 데이터를 기간별로 조회하여 JSON으로 반환하는 API 뷰입니다.
    """
    start_date_str = request.GET.get('start')
    end_date_str = request.GET.get('end')

    if not start_date_str or not end_date_str:
        return JsonResponse({'error': 'Date range not provided'}, status=400)

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    orders = Order.objects.filter(order_date__date__range=[start_date, end_date])
    status_counts = orders.values('order_status').annotate(count=Count('id'))
    
    data = {'주문접수': 0, '처리중': 0, '출고완료': 0, '배송완료': 0, '주문취소':0, '오류':0}
    status_map = {
        'PENDING': '주문접수', 'PROCESSING': '처리중', 'SHIPPED': '출고완료',
        'DELIVERED': '배송완료', 'CANCELED': '주문취소', 'ERROR': '오류'
    }

    for item in status_counts:
        status_key = status_map.get(item['order_status'])
        if status_key:
            data[status_key] = item['count']

    return JsonResponse({
        'labels': list(data.keys()),
        'data': list(data.values()),
    })

@login_required
def delivery_chart_data(request):
    """
    대시보드의 배송 현황 차트에 필요한 데이터를 JSON으로 반환하는 API 뷰입니다.
    """
    data = {'집하완료': 12, '배송중': 8, '배송완료': 30}
    return JsonResponse(data)


# ----------------------------------------
# 인증 (로그인/로그아웃/회원가입) 뷰
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
# 페이지 렌더링 뷰 (함수 기반)
# ----------------------------------------

@login_required
def dashboard(request):
    context = {'page_title': '홈', 'active_menu': 'dashboard'}
    return render(request, 'wms_app/dashboard.html', context)

@login_required
def order_manage(request):
    context = {'page_title': '주문 관리', 'active_menu': 'orders'}
    return render(request, 'wms_app/order_manage.html', context)

# --- [신규] 통합 관리 페이지를 위한 뷰 함수 ---
@login_required
def management_dashboard(request):
    """
    정산, 센터, 화주사, 택배사 등 각종 관리 기능을 모아 보여주는
    통합 관리 대시보드 페이지를 렌더링합니다.
    """
    # 상단에 표시할 요약 정보를 계산합니다.
    context = {
        'page_title': '통합 관리',
        'active_menu': 'management',
        'shipper_count': Shipper.objects.count(),
        'product_count': Product.objects.count(),
        'center_count': Center.objects.count(),
        'courier_count': Courier.objects.count(),
    }
    return render(request, 'wms_app/management_dashboard.html', context)
# -----------------------------------------

@login_required
def stock_manage(request):
    queryset = Product.objects.select_related('shipper__center').all()
    
    selected_center = request.session.get('selected_center')
    selected_shipper = request.session.get('selected_shipper')
    
    if selected_center:
        queryset = queryset.filter(shipper__center__name=selected_center)
    if selected_shipper:
        queryset = queryset.filter(shipper__name=selected_shipper)
        
    context = {
        'page_title': '재고관리',
        'object_list': queryset,
        'columns': [
            {'header': '상품명', 'key': 'name'},
            {'header': '크기(cm)', 'is_size': True},
            {'header': '재고', 'key': 'quantity'},
            {'header': '바코드', 'key': 'barcode'},
            {'header': '화주사명', 'key': 'shipper'},
        ],
        'active_menu': 'management',
        'update_url_name': 'stock_update',
    }
    return render(request, 'wms_app/generic_list.html', context)

@login_required
@transaction.atomic
def stock_io_view(request):
    if request.method == 'POST':
        form_data = request.POST.copy()
        form_data['product'] = request.POST.get('product')
        form = StockIOForm(form_data)
        
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            memo = form.cleaned_data['memo']
            io_type = request.POST.get('io_type')

            if io_type == 'in':
                product.quantity = F('quantity') + quantity
                movement_type = 'IN'
            elif io_type == 'out':
                product.refresh_from_db()
                if product.quantity < quantity:
                    return HttpResponseBadRequest("재고가 부족합니다.")
                product.quantity = F('quantity') - quantity
                movement_type = 'OUT'
            
            product.save()
            
            StockMovement.objects.create(
                product=product, movement_type=movement_type,
                quantity=quantity, memo=memo
            )
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
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('stock_manage')
    else:
        form = StockUpdateForm(instance=product)
    
    context = {
        'form': form, 'product': product,
        'page_title': '재고 수량 수정', 'active_menu': 'management'
    }
    return render(request, 'wms_app/stock_update_form.html', context)

@login_required
def stock_movement_history(request):
    movements = StockMovement.objects.select_related('product__shipper').order_by('-timestamp')
    context = {
        'page_title': '입출고 기록', 'movements': movements,
        'active_menu': 'inout'
    }
    return render(request, 'wms_app/stock_history.html', context)

@login_required
def user_manage(request):
    user_list = User.objects.filter(is_superuser=False)
    context = {
        'page_title': '사용자 관리',
        'active_menu': 'management',
        'user_list': user_list,
    }
    return render(request, 'wms_app/user_list.html', context)

@login_required
def user_update(request, pk):
    user_instance = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_instance)
        if form.is_valid():
            form.save()
            return redirect('user_manage')
    else:
        form = UserUpdateForm(instance=user_instance)
    
    context = {
        'form': form, 'target_user': user_instance,
        'page_title': '사용자 역할 및 소속 수정', 'active_menu': 'management',
    }
    return render(request, 'wms_app/user_form.html', context)

# --- [임시] 기능 개발 예정 페이지 ---
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

# ----------------------------------------
# 기준정보 관리 뷰 (클래스 기반)
# ----------------------------------------
class CenterListView(LoginRequiredMixin, ListView):
    model = Center
    template_name = 'wms_app/generic_list.html'
    context_object_name = 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '센터 관리',
            'columns': [{'header': '센터명', 'key': 'name'}, {'header': '주소', 'key': 'address'}],
            'create_url': reverse_lazy('center_create'),
            'update_url_name': 'center_update',
            'delete_url_name': 'center_delete',
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
            'page_title': '화주사 관리',
            'columns': [{'header': '화주사명', 'key': 'name'}, {'header': '담당자', 'key': 'contact'}, {'header': '소속 센터', 'key': 'center'}],
            'create_url': reverse_lazy('shipper_create'),
            'update_url_name': 'shipper_update',
            'delete_url_name': 'shipper_delete',
            'extra_actions': [{'label': '판매 상품', 'url_name': 'shipper_product_list', 'class': 'btn-info'}],
            'active_menu': 'management'
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
            'page_title': '택배사 관리',
            'columns': [{'header': '택배사명', 'key': 'name'}, {'header': '연락처', 'key': 'contact'}],
            'create_url': reverse_lazy('courier_create'),
            'update_url_name': 'courier_update',
            'delete_url_name': 'courier_delete',
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

# --- 화주사별 상품 관리 뷰 ---
@login_required
def shipper_product_list(request, shipper_pk):
    shipper = get_object_or_404(Shipper, pk=shipper_pk)
    products = Product.objects.filter(shipper=shipper)
    context = {
        'shipper': shipper, 'products': products,
        'page_title': f'{shipper.name} 판매 상품', 'active_menu': 'management'
    }
    return render(request, 'wms_app/shipper_product_list.html', context)

@login_required
def shipper_product_create(request, shipper_pk):
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
    context = {
        'form': form, 'shipper': shipper,
        'page_title': f'{shipper.name} 상품 등록', 'active_menu': 'management'
    }
    return render(request, 'wms_app/shipper_product_form.html', context)

@login_required
def shipper_product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('shipper_product_list', shipper_pk=product.shipper.pk)
    else:
        form = ProductForm(instance=product)
    context = {
        'form': form,
        'page_title': '판매 상품 편집', 'active_menu': 'management'
    }
    return render(request, 'wms_app/shipper_product_form.html', context)

@login_required
def shipper_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    shipper_pk = product.shipper.pk
    if request.method == 'POST':
        product.delete()
        return redirect('shipper_product_list', shipper_pk=shipper_pk)
    return HttpResponseBadRequest("잘못된 요청입니다.")

# ----------------------------------------
# 컨텍스트 프로세서
# ----------------------------------------
def filters(request):
    selected_center_name = request.session.get('selected_center', '')

    shippers = Shipper.objects.all()
    if selected_center_name:
        shippers = shippers.filter(center__name=selected_center_name)

    return {
        'centers': Center.objects.all(),
        'shippers': shippers,
        'selected_center': selected_center_name,
        'selected_shipper': request.session.get('selected_shipper', ''),
    }

# ----------------------------------------
# 엑셀 주문 등록 뷰 (디버깅 코드가 추가된 최종 수정본)
# ----------------------------------------

@login_required
def order_excel_upload(request):
    """
    엑셀 파일을 업로드 받아 주문을 일괄 등록하는 뷰입니다.
    """
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            messages.error(request, '엑셀 파일을 선택해주세요.')
            return redirect('order_manage')
        
        # --- [디버깅용 코드] ---
        print("--- [DEBUG] 엑셀 파일 업로드 시작 ---")
        # --------------------

        try:
            wb = openpyxl.load_workbook(excel_file, data_only=True)
            sheet = wb.active
            
            orders_data = {}
            new_orders_to_create = []

            print(f"--- [DEBUG] 총 {sheet.max_row - 1}개의 데이터 행을 읽기 시작합니다. ---")

            for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                if not any(row):
                    continue

                # --- [디버깅용 코드] ---
                print(f"--- [DEBUG] {row_idx}번째 행 데이터: {row} ---")
                # --------------------

                order_no = str(row[0]).strip() if row[0] else None
                shipper_name = str(row[1]).strip() if row[1] else None
                channel_name = str(row[2]).strip() if row[2] else None
                recipient_name = str(row[3]).strip() if row[3] else None
                recipient_phone = str(row[4]).strip() if row[4] else ''
                address = str(row[5]).strip() if row[5] else ''
                product_identifier = str(row[6]).strip() if row[6] else None
                quantity = int(row[7]) if row[7] else 0

                if not all([shipper_name, channel_name, product_identifier, quantity > 0]):
                    messages.warning(request, f'{row_idx}번째 행의 필수 정보(화주사, 채널, 상품, 수량)가 누락되어 건너뜁니다.')
                    continue

                item_info = {'product_identifier': product_identifier, 'quantity': quantity, 'row_idx': row_idx}
                
                if order_no:
                    if order_no not in orders_data:
                        orders_data[order_no] = {
                            'shipper_name': shipper_name, 'channel_name': channel_name,
                            'recipient_name': recipient_name, 'recipient_phone': recipient_phone, 'address': address,
                            'items': []
                        }
                    orders_data[order_no]['items'].append(item_info)
                else:
                    new_orders_to_create.append({
                        'shipper_name': shipper_name, 'channel_name': channel_name,
                        'recipient_name': recipient_name, 'recipient_phone': recipient_phone, 'address': address,
                        'item': item_info
                    })
            
            print("--- [DEBUG] 엑셀 파일 파싱 완료. 데이터베이스 저장을 시작합니다. ---")

            with transaction.atomic():
                def find_product(identifier, shipper, row_idx):
                    product_query = Product.objects.filter(
                        Q(barcode=identifier) | Q(name=identifier),
                        shipper=shipper
                    )
                    
                    print(f"--- [DEBUG] '{identifier}' 상품 조회 시도... (화주사: {shipper.name}) ---")
                    
                    if product_query.count() == 1:
                        product = product_query.first()
                        print(f"--- [DEBUG] 상품 찾음: {product.name} ---")
                        return product
                    elif product_query.count() > 1:
                        raise Exception(f"{row_idx}번째 행의 상품 '{identifier}'이(가) 해당 화주사에 여러 개 존재하여 특정할 수 없습니다.")
                    else:
                        raise Product.DoesNotExist(f"{row_idx}번째 행의 상품 '{identifier}'을(를) 찾을 수 없습니다.")

                # 주문번호가 있는 주문들 처리
                for order_no, data in orders_data.items():
                    shipper = get_object_or_404(Shipper, name=data['shipper_name'])
                    channel, _ = SalesChannel.objects.get_or_create(name=data['channel_name'])
                    
                    order, created = Order.objects.get_or_create(
                        shipper=shipper, order_no=order_no,
                        defaults={
                            'channel': channel, 'recipient_name': data['recipient_name'],
                            'recipient_phone': data['recipient_phone'], 'address': data['address'],
                            'order_date': datetime.now(), 'order_status': 'PENDING'
                        }
                    )
                    
                    if created:
                        print(f"--- [DEBUG] 주문 생성됨: {order.order_no} ---")
                        for item_data in data['items']:
                            product = find_product(item_data['product_identifier'], shipper, item_data['row_idx'])
                            OrderItem.objects.create(order=order, product=product, quantity=item_data['quantity'])

                # 주문번호가 없는 신규 주문들 처리
                for data in new_orders_to_create:
                    shipper = get_object_or_404(Shipper, name=data['shipper_name'])
                    channel, _ = SalesChannel.objects.get_or_create(name=data['channel_name'])
                    
                    order = Order.objects.create(
                        shipper=shipper,
                        channel=channel,
                        recipient_name=data['recipient_name'],
                        recipient_phone=data['recipient_phone'],
                        address=data['address'],
                        order_date=datetime.now(),
                        order_status='PENDING'
                    )
                    print(f"--- [DEBUG] 신규 주문 생성됨 (자동번호): {order.order_no} ---")
                    
                    product = find_product(data['item']['product_identifier'], shipper, data['item']['row_idx'])
                    OrderItem.objects.create(order=order, product=product, quantity=data['item']['quantity'])
            
            total_created_count = len(orders_data) + len(new_orders_to_create)
            if total_created_count > 0:
                messages.success(request, f'{total_created_count}개의 주문이 성공적으로 등록되었습니다.')
            print("--- [DEBUG] 모든 작업이 성공적으로 완료되었습니다. ---")

        except Exception as e:
            # --- [디버깅용 코드] ---
            print(f"!!!!!!!!!!!!!!! [ERROR] !!!!!!!!!!!!!!!")
            print(f"엑셀 업로드 중 오류가 발생했습니다: {e}")
            import traceback
            traceback.print_exc() # 상세한 오류 내역 출력
            print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            # --------------------
            messages.error(request, f'주문 등록 중 오류 발생: {e}')

        return redirect('order_manage')

    return redirect('order_manage')