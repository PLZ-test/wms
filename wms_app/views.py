from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Sum, F, Count
from datetime import datetime
from django.db import transaction

# --- [수정] 인증 관련 모듈 import ---
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages

from .models import Center, Shipper, Courier, Product, Order, StockMovement, User
# --- [수정] CustomUserCreationForm 추가 ---
from .forms import CenterForm, ShipperForm, CourierForm, ProductForm, StockIOForm, StockUpdateForm, UserUpdateForm, CustomUserCreationForm


# --- [추가] 인증(로그인, 회원가입) 관련 뷰 ---
class CustomLoginView(LoginView):
    """
    사용자 정의 로그인 뷰.
    로그인 실패 시 메시지를 추가하고, is_active가 False인 사용자는 로그인하지 못하게 합니다.
    """
    template_name = 'registration/login.html'

    def form_invalid(self, form):
        # 로그인 실패 시 처리 (아이디, 비밀번호 틀림)
        messages.error(self.request, '아이디 또는 비밀번호가 올바르지 않습니다.')
        return super().form_invalid(form)
    
    def form_valid(self, form):
        user = form.get_user()
        # 계정이 비활성화 상태인 경우
        if not user.is_active:
            messages.error(self.request, '아직 승인되지 않은 계정입니다. 관리자에게 문의하세요.')
            return self.form_invalid(form)
        return super().form_valid(form)

def signup_view(request):
    """
    회원가입 뷰.
    새로운 사용자 계정을 생성하고, is_active=False로 설정하여 관리자 승인을 대기하게 합니다.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('signup_done')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def signup_done_view(request):
    """회원가입 완료 페이지 뷰."""
    return render(request, 'registration/signup_done.html')


# --- [수정] 기존 뷰들에 @login_required 추가 ---
@login_required
def dashboard(request):
    """대시보드 페이지 뷰. 현재 필터 상태를 함께 전달합니다."""
    context = {'page_title': '대시보드', 'active_menu': 'dashboard'}
    return render(request, 'wms_app/dashboard.html', context)

@login_required
def order_chart_data(request):
    """
    주문 현황 차트 데이터 API.
    GET 파라미터(start, end)로 받은 기간 동안의 주문 상태별 건수를 반환합니다.
    """
    start_date_str = request.GET.get('start')
    end_date_str = request.GET.get('end')

    if not start_date_str or not end_date_str:
        return JsonResponse({'error': 'Date range not provided'}, status=400)

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    orders = Order.objects.filter(order_date__range=[start_date, end_date])
    status_counts = orders.values('order_status').annotate(count=Count('id'))

    data = {'준비중': 0, '완료': 0, '취소': 0}
    for item in status_counts:
        data[item['order_status']] = item['count']

    return JsonResponse({
        'labels': list(data.keys()),
        'data': list(data.values()),
    })

@login_required
def delivery_chart_data(request):
    """
    배송 현황 차트 데이터 API.
    GET 파라미터(start, end)로 받은 기간 동안의 배송 상태별 건수를 반환합니다.
    """
    start_date_str = request.GET.get('start')
    end_date_str = request.GET.get('end')

    if not start_date_str or not end_date_str:
        return JsonResponse({'error': 'Date range not provided'}, status=400)

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    orders = Order.objects.filter(delivery_date__range=[start_date, end_date])
    status_counts = orders.values('delivery_status').annotate(count=Count('id')).exclude(delivery_status='')

    data = {'집하완료': 0, '배송중': 0, '배송완료': 0}
    for item in status_counts:
        if item['delivery_status'] in data:
            data[item['delivery_status']] = item['count']

    return JsonResponse(data)

@login_required
def stock_manage(request):
    """
    재고 관리 페이지 뷰.
    세션에 저장된 필터 값에 따라 재고 목록을 필터링하여 표시합니다.
    """
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
    """
    재고 입출고 처리 뷰.
    입고 시 재고를 증가시키고, 출고 시 재고를 감소시킵니다.
    재고 부족 시 에러를 반환합니다. 트랜잭션을 사용하여 원자성을 보장합니다.
    """
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
                # 입고: F() 표현식을 사용하여 DB에서 직접 재고 수량을 증가시킵니다.
                product.quantity = F('quantity') + quantity
                movement_type = 'IN'
            elif io_type == 'out':
                # 출고: 현재 재고를 다시 불러와서 부족한지 확인 후 감소시킵니다.
                product.refresh_from_db()
                if product.quantity < quantity:
                    return HttpResponseBadRequest("재고가 부족합니다.")
                product.quantity = F('quantity') - quantity
                movement_type = 'OUT'

            product.save()

            # 재고 이동 기록 생성
            StockMovement.objects.create(
                product=product,
                movement_type=movement_type,
                quantity=quantity,
                memo=memo
            )
            return redirect('stock_io')

    # GET 요청 처리
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
    """재고 수량 수정 뷰."""
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
    """입출고 기록 목록 뷰."""
    movements = StockMovement.objects.select_related('product__shipper').order_by('-timestamp')
    context = {
        'page_title': '입출고 기록',
        'movements': movements,
        'active_menu': 'inout'
    }
    return render(request, 'wms_app/stock_history.html', context)

# --- 아래는 placeholder 및 기타 뷰들 ---
@login_required
def order_manage(request):
    """주문 페이지 (기능 준비 중)"""
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '주문', 'active_menu': 'orders'})

@login_required
def order_manage_new(request):
    """주문 관리 페이지 (기능 준비 중)"""
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '주문 관리', 'active_menu': 'management'})

@login_required
def stock_in(request):
    """입고 페이지 (기능 준비 중)"""
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '입고', 'active_menu': 'inout'})

@login_required
def stock_out(request):
    """출고 페이지 (기능 준비 중)"""
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '출고', 'active_menu': 'inout'})

@login_required
def settlement_status(request):
    """정산 현황 페이지 (기능 준비 중)"""
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '정산 현황', 'active_menu': 'settlement'})

@login_required
def settlement_billing(request):
    """정산 청구내역 페이지 (기능 준비 중)"""
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '정산 청구내역', 'active_menu': 'settlement'})

@login_required
def settlement_config(request):
    """정산내역설정 페이지 (기능 준비 중)"""
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '정산내역설정', 'active_menu': 'settlement'})

@login_required
def user_manage(request):
    """사용자 관리 페이지 뷰. 슈퍼유저를 제외한 모든 사용자를 표시합니다."""
    # is_superuser가 아닌 모든 사용자를 조회합니다.
    user_list = User.objects.filter(is_superuser=False)
    context = {
        'page_title': '사용자 관리',
        'active_menu': 'management',
        'user_list': user_list,
    }
    return render(request, 'wms_app/user_list.html', context)

@login_required
def user_update(request, pk):
    """사용자 역할 및 소속 수정 뷰."""
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

# --- [수정] 클래스 기반 뷰에 LoginRequiredMixin 추가 ---
class CenterListView(LoginRequiredMixin, ListView):
    """센터 목록을 보여주는 뷰."""
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
    """새로운 센터를 등록하는 뷰."""
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
    """기존 센터 정보를 수정하는 뷰."""
    model = Center
    form_class = CenterForm
    template_name = 'wms_app/generic_form.html'
    success_url = reverse_lazy('center_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '센터 편집'
        context['active_menu'] = 'management'
        context['delete_url_name'] = 'center_delete'
        return context

class CenterDeleteView(LoginRequiredMixin, DeleteView):
    """센터를 삭제하는 뷰."""
    model = Center
    success_url = reverse_lazy('center_list')

class ShipperListView(LoginRequiredMixin, ListView):
    """화주사 목록을 보여주는 뷰. 필터링 기능이 포함됩니다."""
    model = Shipper
    template_name = 'wms_app/generic_list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('center')
        selected_center = self.request.session.get('selected_center')
        selected_shipper = self.request.session.get('selected_shipper')

        if selected_center:
            queryset = queryset.filter(center__name=selected_center)
        if selected_shipper:
            queryset = queryset.filter(name=selected_shipper)

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
    """새로운 화주사를 등록하는 뷰."""
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
    """기존 화주사 정보를 수정하는 뷰."""
    model = Shipper
    form_class = ShipperForm
    template_name = 'wms_app/generic_form.html'
    success_url = reverse_lazy('shipper_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '화주사 편집'
        context['active_menu'] = 'management'
        context['delete_url_name'] = 'shipper_delete'
        return context

class ShipperDeleteView(LoginRequiredMixin, DeleteView):
    """화주사를 삭제하는 뷰."""
    model = Shipper
    success_url = reverse_lazy('shipper_list')

class CourierListView(LoginRequiredMixin, ListView):
    """택배사 목록을 보여주는 뷰."""
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
    """새로운 택배사를 등록하는 뷰."""
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
    """기존 택배사 정보를 수정하는 뷰."""
    model = Courier
    form_class = CourierForm
    template_name = 'wms_app/generic_form.html'
    success_url = reverse_lazy('courier_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '택배사 편집'
        context['active_menu'] = 'management'
        context['delete_url_name'] = 'courier_delete'
        return context

class CourierDeleteView(LoginRequiredMixin, DeleteView):
    """택배사를 삭제하는 뷰."""
    model = Courier
    success_url = reverse_lazy('courier_list')

@login_required
def shipper_product_list(request, shipper_pk):
    """특정 화주사의 상품 목록을 보여주는 뷰."""
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
    """특정 화주사의 상품을 등록하는 뷰."""
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
        'form': form,
        'shipper': shipper,
        'page_title': f'{shipper.name} 상품 등록',
        'active_menu': 'management'
    }
    return render(request, 'wms_app/shipper_product_form.html', context)

@login_required
def shipper_product_update(request, pk):
    """특정 상품의 정보를 수정하는 뷰."""
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
    """특정 상품을 삭제하는 뷰."""
    product = get_object_or_404(Product, pk=pk)
    shipper_pk = product.shipper.pk
    if request.method == 'POST':
        product.delete()
        return redirect('shipper_product_list', shipper_pk=shipper_pk)
    return HttpResponseBadRequest("잘못된 요청입니다.")


def filters(request):
    """템플릿에서 공통으로 사용되는 필터 데이터를 제공하는 컨텍스트 프로세서."""
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