# management/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest

from .models import Center, Shipper, Courier, Product
from .forms import CenterForm, ShipperForm, CourierForm, ProductForm


@login_required
def management_dashboard(request):
    """
    통합 관리 대시보드 뷰
    """
    context = {
        'page_title': '통합 관리',
        'active_menu': 'management',
        'shipper_count': Shipper.objects.count(),
        'product_count': Product.objects.count(),
        'center_count': Center.objects.count(),
        'courier_count': Courier.objects.count(),
    }
    return render(request, 'management/management_dashboard.html', context)

# --- Center (센터) CRUD 뷰 ---

class CenterListView(LoginRequiredMixin, ListView):
    model = Center
    template_name = 'management/generic_list.html'
    context_object_name = 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '센터 관리',
            'columns': [{'header': '센터명', 'key': 'name'}, {'header': '주소', 'key': 'address'}],
            'create_url': reverse_lazy('management:center_create'),
            'update_url_name': 'management:center_update',
            'delete_url_name': 'management:center_delete',
            'active_menu': 'management'
        })
        return context

class CenterCreateView(LoginRequiredMixin, CreateView):
    model = Center
    form_class = CenterForm
    template_name = 'management/generic_form.html'
    success_url = reverse_lazy('management:center_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '센터 등록'
        context['active_menu'] = 'management'
        return context

class CenterUpdateView(LoginRequiredMixin, UpdateView):
    model = Center
    form_class = CenterForm
    template_name = 'management/generic_form.html'
    success_url = reverse_lazy('management:center_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '센터 편집'
        context['active_menu'] = 'management'
        return context

class CenterDeleteView(LoginRequiredMixin, DeleteView):
    model = Center
    success_url = reverse_lazy('management:center_list')


# --- Shipper (화주사) CRUD 뷰 ---

class ShipperListView(LoginRequiredMixin, ListView):
    model = Shipper
    template_name = 'management/generic_list.html'
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
            'create_url': reverse_lazy('management:shipper_create'),
            'update_url_name': 'management:shipper_update',
            'delete_url_name': 'management:shipper_delete',
            'extra_actions': [{'label': '판매 상품', 'url_name': 'management:product_list', 'class': 'btn-info'}],
            'active_menu': 'management'
        })
        return context

class ShipperCreateView(LoginRequiredMixin, CreateView):
    model = Shipper
    form_class = ShipperForm
    template_name = 'management/generic_form.html'
    success_url = reverse_lazy('management:shipper_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '화주사 등록'
        context['active_menu'] = 'management'
        return context

class ShipperUpdateView(LoginRequiredMixin, UpdateView):
    model = Shipper
    form_class = ShipperForm
    template_name = 'management/generic_form.html'
    success_url = reverse_lazy('management:shipper_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '화주사 편집'
        context['active_menu'] = 'management'
        return context

class ShipperDeleteView(LoginRequiredMixin, DeleteView):
    model = Shipper
    success_url = reverse_lazy('management:shipper_list')


# --- Courier (택배사) CRUD 뷰 ---

class CourierListView(LoginRequiredMixin, ListView):
    model = Courier
    template_name = 'management/generic_list.html'
    context_object_name = 'object_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': '택배사 관리',
            'columns': [{'header': '택배사명', 'key': 'name'}, {'header': '연락처', 'key': 'contact'}],
            'create_url': reverse_lazy('management:courier_create'),
            'update_url_name': 'management:courier_update',
            'delete_url_name': 'management:courier_delete',
            'active_menu': 'management'
        })
        return context

class CourierCreateView(LoginRequiredMixin, CreateView):
    model = Courier
    form_class = CourierForm
    template_name = 'management/generic_form.html'
    success_url = reverse_lazy('management:courier_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '택배사 등록'
        context['active_menu'] = 'management'
        return context

class CourierUpdateView(LoginRequiredMixin, UpdateView):
    model = Courier
    form_class = CourierForm
    template_name = 'management/generic_form.html'
    success_url = reverse_lazy('management:courier_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '택배사 편집'
        context['active_menu'] = 'management'
        return context

class CourierDeleteView(LoginRequiredMixin, DeleteView):
    model = Courier
    success_url = reverse_lazy('management:courier_list')


# --- Product (상품) CRUD 뷰 ---

@login_required
def product_list_view(request, shipper_pk):
    """
    특정 화주사의 상품 목록을 보여주는 뷰
    """
    shipper = get_object_or_404(Shipper, pk=shipper_pk)
    products = Product.objects.filter(shipper=shipper)
    context = {
        'shipper': shipper,
        'products': products,
        'page_title': f'{shipper.name} 판매 상품',
        'active_menu': 'management'
    }
    return render(request, 'management/shipper_product_list.html', context)

@login_required
def product_create_view(request, shipper_pk):
    """
    특정 화주사의 상품을 등록하는 뷰
    """
    shipper = get_object_or_404(Shipper, pk=shipper_pk)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.shipper = shipper
            product.save()
            return redirect('management:product_list', shipper_pk=shipper.pk)
    else:
        form = ProductForm()
    context = {
        'form': form,
        'shipper': shipper,
        'page_title': f'{shipper.name} 상품 등록',
        'active_menu': 'management'
    }
    return render(request, 'management/shipper_product_form.html', context)

@login_required
def product_update_view(request, pk):
    """
    상품 정보를 수정하는 뷰
    """
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('management:product_list', shipper_pk=product.shipper.pk)
    else:
        form = ProductForm(instance=product)
    context = {
        'form': form,
        'page_title': '판매 상품 편집',
        'active_menu': 'management'
    }
    return render(request, 'management/shipper_product_form.html', context)

@login_required
def product_delete_view(request, pk):
    """
    상품을 삭제하는 뷰
    """
    product = get_object_or_404(Product, pk=pk)
    shipper_pk = product.shipper.pk
    if request.method == 'POST':
        product.delete()
        return redirect('management:product_list', shipper_pk=shipper_pk)
    # POST 요청이 아닐 경우 잘못된 요청으로 처리
    return HttpResponseBadRequest("잘못된 요청입니다.")