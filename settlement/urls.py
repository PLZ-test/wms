# settlement/urls.py
from django.urls import path
from . import views

app_name = 'settlement'

urlpatterns = [
    path('status/', views.settlement_status_view, name='status'),
    path('billing/', views.settlement_billing_view, name='billing'),
    path('config/', views.settlement_config_view, name='config'),
]