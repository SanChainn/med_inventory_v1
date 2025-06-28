# inventory/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db import transaction
from django.db.models import Sum, F
from django.http import JsonResponse
import json
from django.contrib import messages

from .models import Medicine, Sale, SaleItem
from .forms import MedicineForm

class MedicineListView(ListView):
    model = Medicine
    template_name = 'inventory/medicine_list.html'
    context_object_name = 'medicines'

class MedicineCreateView(CreateView):
    model = Medicine
    form_class = MedicineForm
    template_name = 'inventory/medicine_form.html'
    success_url = reverse_lazy('medicine_list')

    def form_invalid(self, form):
        messages.error(self.request, "There was an error saving the medicine. Please check the form.")
        return super().form_invalid(form)

class MedicineUpdateView(UpdateView):
    model = Medicine
    form_class = MedicineForm
    template_name = 'inventory/medicine_form.html'
    success_url = reverse_lazy('medicine_list')

    def form_invalid(self, form):
        messages.error(self.request, "There was an error updating the medicine. Please check the form.")
        return super().form_invalid(form)

class MedicineDeleteView(DeleteView):
    model = Medicine
    template_name = 'inventory/medicine_confirm_delete.html'
    success_url = reverse_lazy('medicine_list')

def pos_view(request):
    if request.method == 'POST':
        try:
            cart_data = json.loads(request.body).get('cart', [])
            if not cart_data:
                return JsonResponse({'status': 'error', 'message': 'Cart is empty.'}, status=400)

            with transaction.atomic():
                sale = Sale.objects.create()
                for item_data in cart_data:
                    medicine = Medicine.objects.get(pk=item_data['id'])
                    quantity_sold = int(item_data['quantity'])

                    if medicine.quantity < quantity_sold:
                        raise ValueError(f"Not enough stock for {medicine.name}.")

                    SaleItem.objects.create(
                        sale=sale,
                        medicine=medicine,
                        quantity=quantity_sold,
                        price_at_sale=medicine.selling_price
                    )
                    
                    medicine.quantity = F('quantity') - quantity_sold
                    medicine.save(update_fields=['quantity'])
                
                sale.update_total()

            return JsonResponse({'status': 'success', 'message': 'Sale completed successfully!', 'sale_id': sale.pk})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    medicines = Medicine.objects.filter(quantity__gt=0)
    return render(request, 'inventory/pos.html', {'medicines': medicines})

def sales_report_view(request):
    sales = Sale.objects.all().order_by('-created_at')
    total_revenue = sales.aggregate(total=Sum('total_amount'))['total'] or 0
    return render(request, 'inventory/sales_report.html', {'sales': sales, 'total_revenue': total_revenue})

class SaleDetailView(DetailView):
    model = Sale
    template_name = 'inventory/sale_detail.html'
    context_object_name = 'sale'

def sale_receipt_view(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'inventory/sale_receipt.html', {'sale': sale})
