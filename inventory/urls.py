# inventory/urls.py

from django.urls import path
from .views import (
    MedicineListView,
    MedicineCreateView,
    MedicineUpdateView,
    MedicineDeleteView,
    pos_view,
    sales_report_view,
    SaleDetailView,
    sale_receipt_view,
)

urlpatterns = [
    # CRUD URLs for Medicines
    path('', MedicineListView.as_view(), name='medicine_list'),
    path('new/', MedicineCreateView.as_view(), name='medicine_new'),
    path('<int:pk>/edit/', MedicineUpdateView.as_view(), name='medicine_edit'),
    path('<int:pk>/delete/', MedicineDeleteView.as_view(), name='medicine_delete'),

    # Point of Sale URL
    path('pos/', pos_view, name='pos'),

    # Sales and Receipt URLs
    path('sales/', sales_report_view, name='sales_report'),
    path('sales/<int:pk>/', SaleDetailView.as_view(), name='sale_detail'),
    path('sales/receipt/<int:pk>/', sale_receipt_view, name='sale_receipt'),
]
