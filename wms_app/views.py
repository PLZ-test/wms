# wms_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Sum, F, Count
from datetime import datetime
from django.db import transaction
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .models import Center, Shipper, Courier, Product, Order, StockMovement, User, SalesChannel, OrderItem
from .forms import CenterForm, ShipperForm, CourierForm, ProductForm, StockIOForm, StockUpdateForm, UserUpdateForm, CustomUserCreationForm

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
    # URL 쿼리 파라미터에서 'status' 값을 가져옵니다. (e.g., /api/orders/?status=error)
    status = request.GET.get('status')
    
    # 모든 주문 객체를 기본으로 조회합니다.
    orders = Order.objects.all()

    # status 값에 따라 주문 목록을 필터링합니다.
    if status == 'success':
        # 'ERROR' 상태가 아닌 모든 주문을 '성공'으로 간주합니다.
        orders = orders.exclude(order_status='ERROR')
    elif status == 'error':
        # 'ERROR' 상태인 주문만 필터링합니다.
        orders = orders.filter(order_status='ERROR')
    
    # JSON으로 변환할 파이썬 딕셔너리 리스트를 생성합니다.
    data = []
    for order in orders:
        # 각 주문에 포함된 상품 목록을 만듭니다.
        items = [{'product_name': item.product.name, 'quantity': item.quantity} for item in order.items.all()]
        data.append({
            'id': order.id,
            'order_no': order.order_no,
            'shipper': order.shipper.name if order.shipper else '-', # 화주사가 없는 경우 '-' 표시
            'channel': order.channel.name if order.channel else '-', # 판매채널이 없는 경우 '-' 표시
            'recipient': order.recipient_name,
            'status': order.get_order_status_display(), # 모델에 정의된 상태값('PENDING')을 '주문접수'와 같이 변환
            'error_message': order.error_message,
            'items': items,
        })
    # 최종 데이터를 JSON 형식으로 응답합니다.
    return JsonResponse({'orders': data})

def check_username(request):
    """
    회원가입 시 사용자 아이디(username) 중복 여부를 실시간으로 확인하는 API 뷰입니다.
    """
    # GET 요청 파라미터에서 'username' 값을 가져옵니다.
    username = request.GET.get('username', None)
    # User 모델에서 해당 username(대소문자 무시)을 가진 사용자가 존재하는지 확인합니다.
    is_taken = User.objects.filter(username__iexact=username).exists()
    # 결과를 JSON 형식으로 응답합니다. is_available이 true이면 사용 가능한 아이디입니다.
    data = {'is_available': not is_taken}
    return JsonResponse(data)

@login_required
def order_chart_data(request):
    """
    대시보드의 주문 현황 차트에 필요한 데이터를 기간별로 조회하여 JSON으로 반환하는 API 뷰입니다.
    """
    # URL 파라미터에서 시작일과 종료일을 가져옵니다.
    start_date_str = request.GET.get('start')
    end_date_str = request.GET.get('end')

    # 날짜 값이 없으면 오류 응답을 반환합니다.
    if not start_date_str or not end_date_str:
        return JsonResponse({'error': 'Date range not provided'}, status=400)

    # 문자열 형태의 날짜를 datetime 객체로 변환합니다.
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # 해당 기간 내의 주문 데이터를 필터링합니다. (order_date는 DateTimeField이므로 .date로 날짜만 비교)
    orders = Order.objects.filter(order_date__date__range=[start_date, end_date])
    # 주문 상태(order_status)별로 주문 개수를 집계합니다.
    status_counts = orders.values('order_status').annotate(count=Count('id'))
    
    # 차트에 표시할 기본 데이터 구조를 정의합니다.
    data = {'주문접수': 0, '처리중': 0, '출고완료': 0, '배송완료': 0, '주문취소':0, '오류':0}
    # 모델의 영문 상태값과 차트 라벨(한글)을 매핑합니다.
    status_map = {
        'PENDING': '주문접수', 'PROCESSING': '처리중', 'SHIPPED': '출고완료',
        'DELIVERED': '배송완료', 'CANCELED': '주문취소', 'ERROR': '오류'
    }

    # DB에서 집계한 결과를 순회하며 data 딕셔너리의 값을 업데이트합니다.
    for item in status_counts:
        status_key = status_map.get(item['order_status'])
        if status_key:
            data[status_key] = item['count']

    # Chart.js가 요구하는 형식에 맞춰 JSON으로 응답합니다.
    return JsonResponse({
        'labels': list(data.keys()),
        'data': list(data.values()),
    })

@login_required
def delivery_chart_data(request):
    """
    대시보드의 배송 현황 차트에 필요한 데이터를 JSON으로 반환하는 API 뷰입니다.
    (현재는 임시 데이터를 반환하며, 실제 배송 모델 연동 시 수정이 필요합니다.)
    """
    # 이 함수는 현재 배송 관련 모델이 없으므로, 임시 데이터를 반환합니다.
    # 추후 실제 배송 추적 기능이 추가되면 해당 모델을 조회하도록 수정해야 합니다.
    data = {'집하완료': 12, '배송중': 8, '배송완료': 30}
    return JsonResponse(data)


# ----------------------------------------
# 인증 (로그인/로그아웃/회원가입) 뷰
# ----------------------------------------

def wms_logout_view(request):
    """
    사용자를 로그아웃 처리하고 로그인 페이지로 리디렉션합니다.
    """
    logout(request)
    return redirect('login')

class CustomLoginView(LoginView):
    """
    기본 LoginView를 상속받아 커스텀 메시지를 추가한 로그인 뷰입니다.
    """
    template_name = 'registration/login.html'
    
    def form_invalid(self, form):
        # 폼 유효성 검증 실패 시 (아이디/비밀번호 불일치 등) 에러 메시지를 추가합니다.
        messages.error(self.request, '아이디 또는 비밀번호가 올바르지 않습니다.')
        return super().form_invalid(form)

    def form_valid(self, form):
        # 폼 유효성 검증 성공 후 추가적인 조건을 확인합니다.
        user = form.get_user()
        # 사용자가 비활성(is_active=False) 상태인 경우 로그인을 막고 에러 메시지를 표시합니다.
        if not user.is_active:
            messages.error(self.request, '아직 승인되지 않은 계정입니다. 관리자에게 문의하세요.')
            # form_invalid를 호출하여 로그인 실패 흐름을 따릅니다.
            return self.form_invalid(form)
        return super().form_valid(form)

def signup_view(request):
    """
    회원가입 페이지를 렌더링하고, 사용자 입력을 처리하여 계정을 생성하는 뷰입니다.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save() # 사용자를 생성합니다.
            return redirect('signup_done') # 가입 완료 페이지로 이동합니다.
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def signup_done_view(request):
    """
    회원가입 완료 후 보여주는 정적 페이지 뷰입니다.
    """
    return render(request, 'registration/signup_done.html')


# ----------------------------------------
# 페이지 렌더링 뷰 (함수 기반)
# ----------------------------------------

@login_required
def dashboard(request):
    """ 대시보드 메인 페이지를 렌더링합니다. """
    context = {'page_title': '홈', 'active_menu': 'dashboard'}
    return render(request, 'wms_app/dashboard.html', context)

@login_required
def order_manage(request):
    """ 주문 관리 페이지를 렌더링합니다. """
    context = {'page_title': '주문 관리', 'active_menu': 'orders'}
    return render(request, 'wms_app/order_manage.html', context)

@login_required
def stock_manage(request):
    """
    상품 목록과 현재 재고를 보여주는 재고 관리 페이지를 렌더링합니다.
    """
    # Product와 연관된 Shipper, Center 정보를 함께 조회하여 DB 접근 횟수를 줄입니다(select_related).
    queryset = Product.objects.select_related('shipper__center').all()
    
    # 세션에 저장된 필터링 값(센터, 화주사)을 가져옵니다.
    selected_center = request.session.get('selected_center')
    selected_shipper = request.session.get('selected_shipper')
    
    # 필터링 값이 있으면 쿼리셋에 필터를 적용합니다.
    if selected_center:
        queryset = queryset.filter(shipper__center__name=selected_center)
    if selected_shipper:
        queryset = queryset.filter(shipper__name=selected_shipper)
        
    context = {
        'page_title': '재고관리',
        'object_list': queryset,
        'columns': [ # generic_list.html 템플릿에서 사용할 테이블 컬럼 정보
            {'header': '상품명', 'key': 'name'},
            {'header': '크기(cm)', 'is_size': True},
            {'header': '재고', 'key': 'quantity'},
            {'header': '바코드', 'key': 'barcode'},
            {'header': '화주사명', 'key': 'shipper'},
        ],
        'active_menu': 'management', # 사이드바 메뉴 활성화를 위한 값
        'update_url_name': 'stock_update', # 수정 버튼에 연결될 URL 패턴 이름
    }
    return render(request, 'wms_app/generic_list.html', context)

@login_required
@transaction.atomic # DB 트랜잭션을 적용하여 작업 중 오류 발생 시 롤백
def stock_io_view(request):
    """
    재고의 입고 및 출고를 처리하는 페이지 뷰입니다.
    """
    if request.method == 'POST':
        # form_data를 직접 구성하여 form에 전달
        form_data = request.POST.copy()
        form_data['product'] = request.POST.get('product') # product id를 form_data에 추가
        form = StockIOForm(form_data)
        
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            memo = form.cleaned_data['memo']
            io_type = request.POST.get('io_type') # 'in' 또는 'out'

            if io_type == 'in':
                # 입고 처리: 현재 재고에 수량을 더함
                product.quantity = F('quantity') + quantity
                movement_type = 'IN'
            elif io_type == 'out':
                # 출고 처리 전, 최신 재고 상태를 DB에서 다시 가져옴 (동시성 문제 방지)
                product.refresh_from_db()
                if product.quantity < quantity:
                    return HttpResponseBadRequest("재고가 부족합니다.")
                # 출고 처리: 현재 재고에서 수량을 뺌
                product.quantity = F('quantity') - quantity
                movement_type = 'OUT'
            
            product.save() # 상품의 재고 수량 변경사항을 DB에 저장
            
            # 재고 변동 이력을 StockMovement 모델에 기록
            StockMovement.objects.create(
                product=product, 
                movement_type=movement_type,
                quantity=quantity, 
                memo=memo
            )
            return redirect('stock_io')
            
    products = Product.objects.select_related('shipper__center').all()
    # 상단 필터링 로직 (세션값에 따라 상품 목록 필터링)
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
    """
    개별 상품의 재고 수량을 직접 수정하는 뷰입니다.
    """
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('stock_manage')
    else:
        form = StockUpdateForm(instance=product)
    
    context = {
        'form': form, 
        'product': product,
        'page_title': '재고 수량 수정', 
        'active_menu': 'management'
    }
    return render(request, 'wms_app/stock_update_form.html', context)

@login_required
def stock_movement_history(request):
    """
    모든 상품의 입출고 이력을 최신순으로 보여주는 페이지 뷰입니다.
    """
    movements = StockMovement.objects.select_related('product__shipper').order_by('-timestamp')
    context = {
        'page_title': '입출고 기록', 
        'movements': movements,
        'active_menu': 'inout'
    }
    return render(request, 'wms_app/stock_history.html', context)

@login_required
def user_manage(request):
    """
    시스템 사용자(관리자 제외) 목록을 보여주는 관리 페이지 뷰입니다.
    """
    # 슈퍼유저가 아닌 모든 사용자를 조회합니다.
    user_list = User.objects.filter(is_superuser=False)
    context = {
        'page_title': '사용자 관리',
        'active_menu': 'management',
        'user_list': user_list,
    }
    return render(request, 'wms_app/user_list.html', context)

@login_required
def user_update(request, pk):
    """
    사용자의 역할, 소속, 활성 상태를 수정하는 페이지 뷰입니다.
    """
    user_instance = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_instance)
        if form.is_valid():
            form.save()
            return redirect('user_manage')
    else:
        form = UserUpdateForm(instance=user_instance)
    
    context = {
        'form': form, 
        'target_user': user_instance,
        'page_title': '사용자 역할 및 소속 수정', 
        'active_menu': 'management',
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

# --- 센터(Center) CRUD 뷰 ---
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
    # 별도 템플릿 없이 POST 요청 처리 후 success_url로 리디렉션

# --- 화주사(Shipper) CRUD 뷰 ---
class ShipperListView(LoginRequiredMixin, ListView):
    model = Shipper
    template_name = 'wms_app/generic_list.html'
    context_object_name = 'object_list'
    
    def get_queryset(self):
        # 기본 쿼리셋에 센터 정보를 미리 join(select_related)
        queryset = super().get_queryset().select_related('center')
        # 세션 필터링 적용
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
            # '판매 상품' 버튼과 같이 추가적인 동작을 위한 설정
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

# --- 택배사(Courier) CRUD 뷰 ---
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
    """ 특정 화주사에 속한 상품 목록을 보여줍니다. """
    shipper = get_object_or_404(Shipper, pk=shipper_pk)
    products = Product.objects.filter(shipper=shipper)
    context = {
        'shipper': shipper, 
        'products': products,
        'page_title': f'{shipper.name} 판매 상품', 
        'active_menu': 'management'
    }
    return render(request, 'wms_app/shipper_product_list.html', context)

@login_required
def shipper_product_create(request, shipper_pk):
    """ 특정 화주사의 상품을 새로 등록합니다. """
    shipper = get_object_or_404(Shipper, pk=shipper_pk)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False) # DB에 바로 저장하지 않고 객체만 생성
            product.shipper = shipper # 화주사 정보를 설정
            product.save() # 최종 저장
            return redirect('shipper_product_list', shipper_pk=shipper.pk)
    else:
        form = ProductForm()
    context = {
        'form': form, 
        'shipper': shipper,
        'page_title': f'{shipper.name} 상품 등록', 
        'active_menu': 'management'
    }
    return render(request, 'wms_app/shipper_product_form.html', context)

@login_required
def shipper_product_update(request, pk):
    """ 특정 상품의 정보를 수정합니다. """
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
        'page_title': '판매 상품 편집', 
        'active_menu': 'management'
    }
    return render(request, 'wms_app/shipper_product_form.html', context)

@login_required
def shipper_product_delete(request, pk):
    """ 특정 상품을 삭제합니다. """
    product = get_object_or_404(Product, pk=pk)
    shipper_pk = product.shipper.pk
    if request.method == 'POST':
        product.delete()
        return redirect('shipper_product_list', shipper_pk=shipper_pk)
    # GET 요청 등 비정상적인 접근 차단
    return HttpResponseBadRequest("잘못된 요청입니다.")

# ----------------------------------------
# 컨텍스트 프로세서
# ----------------------------------------

def filters(request):
    """
    모든 템플릿에 공통적으로 필요한 필터 데이터를 제공하는 컨텍스트 프로세서입니다.
    이 함수는 settings.py의 TEMPLATES 설정에 등록되어야 합니다.
    """
    selected_center_name = request.session.get('selected_center', '')

    shippers = Shipper.objects.all()
    # 만약 특정 센터가 선택되었다면, 해당 센터에 소속된 화주사만 필터링합니다.
    if selected_center_name:
        shippers = shippers.filter(center__name=selected_center_name)

    # 이 함수가 반환하는 딕셔너리는 모든 템플릿에서 변수처럼 사용할 수 있습니다.
    return {
        'centers': Center.objects.all(),
        'shippers': shippers,
        'selected_center': selected_center_name,
        'selected_shipper': request.session.get('selected_shipper', ''),
    }