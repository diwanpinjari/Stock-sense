from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import StockOperation, StockMoveLine
from .forms import ReceiptCreateForm
from .services import validate_stock_operation


def receipts_list(request):
    """Render all incoming vendor receipts from SQLite."""
    receipts = StockOperation.objects.filter(
        operation_type='receipt'
    ).select_related('source_location', 'destination_location').prefetch_related('lines__product').order_by('-created_at')

    return render(request, 'operations/receipts.html', {'receipts': receipts})


def receipt_create(request):
    """Process receipt creation form."""
    if request.method == 'POST':
        form = ReceiptCreateForm(request.POST)
        if form.is_valid():
            receipt = StockOperation.objects.create(
                operation_type='receipt',
                source_location=form.cleaned_data['source_location'],
                destination_location=form.cleaned_data['destination_location'],
                status='draft',
                notes=form.cleaned_data['notes']
            )
            StockMoveLine.objects.create(
                operation=receipt,
                product=form.cleaned_data['product'],
                quantity=form.cleaned_data['quantity']
            )
            messages.success(request, f"Draft receipt {receipt.reference} created successfully!")
            return redirect('receipts_list')
    else:
        form = ReceiptCreateForm()

    return render(request, 'operations/receipt_create.html', {'form': form})


def receipt_validate(request, pk):
    """Atomically commit inventory movement to the ledger."""
    if request.method == 'POST':
        receipt = get_object_or_404(StockOperation, pk=pk, operation_type='receipt')
        try:
            validate_stock_operation(receipt)
            messages.success(request, f"Receipt {receipt.reference} validated! Stock posted to ledger.")
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))

    return redirect('receipts_list')