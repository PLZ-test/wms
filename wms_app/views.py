from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Sum, F, Count
from datetime import datetime
from django.db import transaction
# from django.views.decorators.http import require_POST # 삭제 기능이 없어졌으므로 이 줄을 삭제하거나 주석 처리합니다.

from .models import *
from .forms import *


# --- 대시보드 ---
def dashboard(request):
    context = {'page_title': '대시보드', 'active_menu': 'dashboard'}
    return render(request, 'wms_app/dashboard.html', context)

def order_chart_data(request):
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

def delivery_chart_data(request):
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


# --- 재고 관리 ---
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
                product=product,
                movement_type=movement_type,
                quantity=quantity,
                memo=memo
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
        'form': form,
        'product': product,
        'page_title': '재고 수량 수정',
        'active_menu': 'management'
    }
    return render(request, 'wms_app/stock_update_form.html', context)

def stock_movement_history(request):
    movements = StockMovement.objects.select_related('product__shipper').order_by('-timestamp')
    context = {
        'page_title': '입출고 기록',
        'movements': movements,
        'active_menu': 'inout'
    }
    return render(request, 'wms_app/stock_history.html', context)

# --- 아래 stock_history_delete 함수를 삭제합니다 ---
# @require_POST
# def stock_history_delete(request, pk):
#     movement = get_object_or_404(StockMovement, pk=pk)
#     movement.delete()
#     return redirect('stock_history')


# --- 임시 페이지 뷰 (Placeholder Views) ---
def order_manage(request):
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '주문', 'active_menu': 'orders'})

def order_manage_new(request):
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '주문 관리', 'active_menu': 'management'})

def stock_in(request):
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '입고', 'active_menu': 'inout'})

def stock_out(request):
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '출고', 'active_menu': 'inout'})

def settlement_status(request):
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '정산 현황', 'active_menu': 'settlement'})

def settlement_billing(request):
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '정산 청구내역', 'active_menu': 'settlement'})

def settlement_config(request):
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '정산내역설정', 'active_menu': 'settlement'})

def user_manage(request):
    return render(request, 'wms_app/placeholder_page.html', {'page_title': '사용자관리', 'active_menu': 'management'})


# --- 설정: 클래스 기반 뷰 (CRUD) ---
class CenterListView(ListView):
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

class CenterCreateView(CreateView):
    model = Center
    form_class = CenterForm
    template_name = 'wms_app/generic_form.html'
    success_url = reverse_lazy('center_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '센터 등록'
        context['active_menu'] = 'management'
        return context

class CenterUpdateView(UpdateView):
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

class CenterDeleteView(DeleteView):
    model = Center
    success_url = reverse_lazy('center_list')

class ShipperListView(ListView):
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

class ShipperCreateView(CreateView):
    model = Shipper
    form_class = ShipperForm
    template_name = 'wms_app/generic_form.html'
    success_url = reverse_lazy('shipper_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '화주사 등록'
        context['active_menu'] = 'management'
        return context

class ShipperUpdateView(UpdateView):
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

class ShipperDeleteView(DeleteView):
    model = Shipper
    success_url = reverse_lazy('shipper_list')

class CourierListView(ListView):
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

class CourierCreateView(CreateView):
    model = Courier
    form_class = CourierForm
    template_name = 'wms_app/generic_form.html'
    success_url = reverse_lazy('courier_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '택배사 등록'
        context['active_menu'] = 'management'
        return context

class CourierUpdateView(UpdateView):
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

class CourierDeleteView(DeleteView):
    model = Courier
    success_url = reverse_lazy('courier_list')

# --- 화주사별 상품 관리 ---
def shipper_product_list(request, shipper_pk):
    shipper = get_object_or_404(Shipper, pk=shipper_pk)
    products = Product.objects.filter(shipper=shipper)
    context = {
        'shipper': shipper,
        'products': products,
        'page_title': f'{shipper.name} 판매 상품',
        'active_menu': 'management'
    }
    return render(request, 'wms_app/shipper_product_list.html', context)

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
        'form': form,
        'shipper': shipper,
        'page_title': f'{shipper.name} 상품 등록',
        'active_menu': 'management'
    }
    return render(request, 'wms_app/shipper_product_form.html', context)

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
        'page_title': '판매 상품 편집',
        'active_menu': 'management'
    }
    return render(request, 'wms_app/shipper_product_form.html', context)

def shipper_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    shipper_pk = product.shipper.pk
    if request.method == 'POST':
        product.delete()
        return redirect('shipper_product_list', shipper_pk=shipper_pk)
    return HttpResponseBadRequest("잘못된 요청입니다.")

# --- 컨텍스트 프로세서 ---
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